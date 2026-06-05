from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Doctor, Appointment, MedicalRecord, Feedback, PatientProfile
from .forms import (PatientRegistrationForm, PatientProfileForm, AppointmentBookingForm,
                    AppointmentUpdateForm, FeedbackForm, DoctorForm, MedicalRecordForm)
import datetime


# ─── Public Views ────────────────────────────────────────────────────────────

def home(request):
    doctors = Doctor.objects.filter(is_active=True)[:6]
    total_doctors = Doctor.objects.filter(is_active=True).count()
    total_patients = User.objects.filter(is_staff=False).count()
    total_appointments = Appointment.objects.count()
    return render(request, 'appointments/home.html', {
        'doctors': doctors,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'appointments/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'admin_dashboard' if user.is_staff else 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'appointments/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def doctor_list(request):
    doctors = Doctor.objects.filter(is_active=True)
    specialization = request.GET.get('specialization', '')
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    specializations = Doctor.objects.values_list('specialization', flat=True).distinct()
    return render(request, 'appointments/doctor_list.html', {
        'doctors': doctors,
        'specializations': specializations,
        'selected': specialization,
    })


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            if request.user.is_authenticated:
                fb.user = request.user
            fb.save()
            messages.success(request, 'Thank you for your feedback! We will respond shortly.')
            return redirect('feedback')
    else:
        form = FeedbackForm()
        if request.user.is_authenticated:
            form.fields['name'].initial = request.user.get_full_name()
            form.fields['email'].initial = request.user.email
    return render(request, 'appointments/feedback.html', {'form': form})


# ─── Patient Views ────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    appointments = Appointment.objects.filter(patient=request.user).order_by('-appointment_date')[:5]
    records = MedicalRecord.objects.filter(patient=request.user)[:3]
    pending = Appointment.objects.filter(patient=request.user, status='pending').count()
    approved = Appointment.objects.filter(patient=request.user, status='approved').count()
    return render(request, 'appointments/dashboard.html', {
        'appointments': appointments,
        'records': records,
        'pending': pending,
        'approved': approved,
    })


@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = request.user
            appt.save()
            messages.success(request, 'Appointment booked successfully! Awaiting approval.')
            return redirect('my_appointments')
    else:
        doctor_id = request.GET.get('doctor')
        form = AppointmentBookingForm()
        if doctor_id:
            form.fields['doctor'].initial = doctor_id
    return render(request, 'appointments/book_appointment.html', {'form': form})


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
    })


@login_required
def cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if appt.status in ['pending', 'approved']:
        appt.status = 'cancelled'
        appt.save()
        messages.success(request, 'Appointment cancelled.')
    else:
        messages.error(request, 'This appointment cannot be cancelled.')
    return redirect('my_appointments')


@login_required
def medical_history(request):
    records = MedicalRecord.objects.filter(patient=request.user)
    return render(request, 'appointments/medical_history.html', {'records': records})


@login_required
def edit_profile(request):
    profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard')
    else:
        form = PatientProfileForm(instance=profile, user=request.user)
    return render(request, 'appointments/edit_profile.html', {'form': form})


# ─── Admin Views ──────────────────────────────────────────────────────────────

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    total_appointments = Appointment.objects.count()
    pending = Appointment.objects.filter(status='pending').count()
    approved = Appointment.objects.filter(status='approved').count()
    completed = Appointment.objects.filter(status='completed').count()
    cancelled = Appointment.objects.filter(status='cancelled').count()
    total_patients = User.objects.filter(is_staff=False).count()
    total_doctors = Doctor.objects.filter(is_active=True).count()
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:10]
    feedbacks = Feedback.objects.filter(is_read=False).count()
    return render(request, 'appointments/admin_dashboard.html', {
        'total_appointments': total_appointments,
        'pending': pending,
        'approved': approved,
        'completed': completed,
        'cancelled': cancelled,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'recent_appointments': recent_appointments,
        'unread_feedbacks': feedbacks,
    })


@admin_required
def manage_appointments(request):
    appointments = Appointment.objects.select_related('patient', 'doctor').all()
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if search:
        appointments = appointments.filter(
            Q(patient__username__icontains=search) |
            Q(patient__first_name__icontains=search) |
            Q(doctor__name__icontains=search)
        )
    return render(request, 'appointments/manage_appointments.html', {
        'appointments': appointments,
        'status_filter': status_filter,
        'search': search,
    })


@admin_required
def update_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentUpdateForm(request.POST, instance=appt)
        if form.is_valid():
            form.save()
            messages.success(request, f'Appointment #{pk} updated to {appt.status}.')
            return redirect('manage_appointments')
    else:
        form = AppointmentUpdateForm(instance=appt)
    return render(request, 'appointments/update_appointment.html', {'form': form, 'appt': appt})


@admin_required
def manage_doctors(request):
    doctors = Doctor.objects.all()
    return render(request, 'appointments/manage_doctors.html', {'doctors': doctors})


@admin_required
def add_doctor(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor added successfully.')
            return redirect('manage_doctors')
    else:
        form = DoctorForm()
    return render(request, 'appointments/doctor_form.html', {'form': form, 'action': 'Add'})


@admin_required
def edit_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doctor updated successfully.')
            return redirect('manage_doctors')
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'appointments/doctor_form.html', {'form': form, 'action': 'Edit', 'doctor': doctor})


@admin_required
def delete_doctor(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        messages.success(request, 'Doctor removed.')
        return redirect('manage_doctors')
    return render(request, 'appointments/confirm_delete.html', {'object': doctor, 'type': 'Doctor'})


@admin_required
def manage_patients(request):
    patients = User.objects.filter(is_staff=False).select_related('patient_profile')
    search = request.GET.get('search', '')
    if search:
        patients = patients.filter(Q(username__icontains=search) | Q(first_name__icontains=search) | Q(email__icontains=search))
    return render(request, 'appointments/manage_patients.html', {'patients': patients, 'search': search})


@admin_required
def manage_records(request):
    records = MedicalRecord.objects.select_related('patient', 'doctor').all()
    return render(request, 'appointments/manage_records.html', {'records': records})


@admin_required
def add_record(request):
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medical record added.')
            return redirect('manage_records')
    else:
        form = MedicalRecordForm()
    return render(request, 'appointments/record_form.html', {'form': form, 'action': 'Add'})


@admin_required
def view_feedbacks(request):
    feedbacks = Feedback.objects.all()
    Feedback.objects.filter(is_read=False).update(is_read=True)
    return render(request, 'appointments/view_feedbacks.html', {'feedbacks': feedbacks})
