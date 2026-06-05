"""
Run this script after migrations to populate the database with demo data:
  python seed_data.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic.settings')
django.setup()

from django.contrib.auth.models import User
from appointments.models import Doctor, PatientProfile, Appointment, MedicalRecord
import datetime

print("Seeding database...")

# Admin user
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@mediclinic.ug', 'admin123')
    admin.first_name = 'System'; admin.last_name = 'Admin'; admin.save()
    print("  ✔ Created admin user (username: admin, password: admin123)")

# Demo patient
if not User.objects.filter(username='jordan').exists():
    patient = User.objects.create_user('jordan', 'jordan@example.com', 'patient123')
    patient.first_name = 'Jordan'; patient.last_name = 'Rukundo'; patient.save()
    PatientProfile.objects.create(
        user=patient, phone='+256 700 123456', gender='Male',
        date_of_birth=datetime.date(2000, 5, 15), blood_group='O+',
        address='Jinja, Uganda', emergency_contact='Parent', emergency_phone='+256 700 999999'
    )
    print("  ✔ Created patient user (username: jordan, password: patient123)")

# Doctors
doctors = [
    {'name': 'Sarah Nakamura', 'specialization': 'General Practice', 'bio': 'Experienced GP with 10+ years.', 'available_days': 'Mon, Tue, Wed, Thu, Fri'},
    {'name': 'James Okonkwo', 'specialization': 'Pediatrics', 'bio': 'Specialist in child healthcare.', 'available_days': 'Mon, Wed, Fri'},
    {'name': 'Aisha Mohammed', 'specialization': 'Cardiology', 'bio': 'Heart specialist with 15 years experience.', 'available_days': 'Tue, Thu'},
    {'name': 'David Ssemwogerere', 'specialization': 'Dermatology', 'bio': 'Skin and hair specialist.', 'available_days': 'Mon, Tue, Thu'},
    {'name': 'Grace Atim', 'specialization': 'Gynecology', 'bio': 'Women\'s health specialist.', 'available_days': 'Mon, Wed, Fri'},
    {'name': 'Peter Mugisha', 'specialization': 'Orthopedics', 'bio': 'Bone and joint specialist.', 'available_days': 'Tue, Thu, Fri'},
]

for d in doctors:
    if not Doctor.objects.filter(name=d['name']).exists():
        Doctor.objects.create(
            name=d['name'], specialization=d['specialization'], bio=d['bio'],
            available_days=d['available_days'],
            available_time_from=datetime.time(8, 0),
            available_time_to=datetime.time(17, 0),
            email=f"{d['name'].split()[0].lower()}@mediclinic.ug",
            is_active=True
        )
        print(f"  ✔ Added Dr. {d['name']}")

# Sample appointments
patient = User.objects.filter(username='jordan').first()
doctor = Doctor.objects.first()
if patient and doctor and not Appointment.objects.filter(patient=patient).exists():
    Appointment.objects.create(
        patient=patient, doctor=doctor,
        appointment_date=datetime.date.today() + datetime.timedelta(days=3),
        appointment_time=datetime.time(10, 0),
        reason='Routine checkup and blood pressure monitoring',
        status='approved'
    )
    Appointment.objects.create(
        patient=patient, doctor=Doctor.objects.all()[1] if Doctor.objects.count() > 1 else doctor,
        appointment_date=datetime.date.today() + datetime.timedelta(days=7),
        appointment_time=datetime.time(14, 30),
        reason='Persistent headaches and dizziness',
        status='pending'
    )
    print("  ✔ Created sample appointments")

# Sample medical record
if patient and doctor and not MedicalRecord.objects.filter(patient=patient).exists():
    MedicalRecord.objects.create(
        patient=patient, doctor=doctor,
        diagnosis='Hypertension Stage 1. Blood pressure: 145/90 mmHg.',
        prescription='Amlodipine 5mg once daily. Low-sodium diet.',
        notes='Patient advised to reduce stress and exercise regularly.',
        visit_date=datetime.date.today() - datetime.timedelta(days=30)
    )
    print("  ✔ Created sample medical record")

print("\n✅ Database seeded successfully!")
print("\nLogin Credentials:")
print("  Admin → username: admin | password: admin123")
print("  Patient → username: jordan | password: patient123")
