# MediClinic – Medical Clinic Appointment Management System
**CSC 1202 – Software Development Project**  
**Student:** Jordan Rukundo Abraham Nzabandora | **Reg:** 25/U/28553/PS  
**Institution:** Makerere University – Jinja Campus | **Year:** 2026

---

## Quick Start (Run Locally in 3 Minutes)

### 1. Install Python & Dependencies
```bash
pip install django==4.2.16 whitenoise==6.7.0
```

### 2. Run Migrations
```bash
cd clinic
python manage.py migrate
```

### 3. Seed Demo Data (doctors, patients, appointments)
```bash
python seed_data.py
```

### 4. Start the Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## Login Credentials

| Role    | Username | Password   | Access                        |
|---------|----------|------------|-------------------------------|
| Admin   | admin    | admin123   | Full admin panel               |
| Patient | jordan   | patient123 | Patient dashboard & booking    |

---

## Pages / Forms Available

| URL                        | Description                              |
|----------------------------|------------------------------------------|
| `/`                        | Home page with stats and doctors         |
| `/register/`               | Patient Registration Form                |
| `/login/`                  | Login Page                               |
| `/dashboard/`              | Patient Dashboard                        |
| `/appointments/book/`      | Book Appointment Form                    |
| `/appointments/my/`        | My Appointments (with status filter)     |
| `/medical-history/`        | Patient Medical History                  |
| `/profile/edit/`           | Edit Patient Profile                     |
| `/doctors/`                | Doctor Schedule / List                   |
| `/feedback/`               | Contact / Feedback Form                  |
| `/admin-dashboard/`        | Admin Dashboard (admin only)             |
| `/admin/appointments/`     | Manage Appointments                      |
| `/admin/doctors/`          | Manage Doctors (add/edit/delete)         |
| `/admin/patients/`         | Manage Patients                          |
| `/admin/records/`          | Medical Records (add/view)               |
| `/admin/feedbacks/`        | View Feedback Messages                   |
| `/admin/`                  | Django built-in admin                    |

---

## Deploy Online (Free, ~5 min)

### Option A – Railway
1. Create account at https://railway.app
2. New Project → Deploy from GitHub (push this folder)
3. Add environment variable: `DJANGO_SETTINGS_MODULE=clinic.settings`
4. Railway auto-detects Python and runs `python manage.py runserver`

### Option B – PythonAnywhere (Free)
1. Create account at https://www.pythonanywhere.com
2. Upload zip, extract, install requirements
3. Configure WSGI to point to `clinic/wsgi.py`
4. Run `python manage.py migrate && python seed_data.py`

### Option C – Render
1. Push to GitHub
2. New Web Service → connect repo
3. Build command: `pip install -r requirements.txt && python manage.py migrate && python seed_data.py`
4. Start command: `python manage.py runserver 0.0.0.0:$PORT`

---

## Tech Stack
- **Backend:** Django 4.2 (Python)
- **Database:** SQLite (bundled, zero config)
- **Frontend:** Bootstrap 5.3 + Font Awesome 6
- **Static Files:** WhiteNoise

