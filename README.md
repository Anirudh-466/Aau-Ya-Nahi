# SmartAttend – Intelligent Student Attendance & Medical Management System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.1+](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![Security: Argon2id](https://img.shields.io/badge/Security-Argon2id-success.svg)](https://en.wikipedia.org/wiki/Argon2)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, responsive, professional, and highly secure **Student Attendance & Medical Management System** built with **Python Flask**, **SQLAlchemy**, **Flask-Login**, **Flask-WTF**, and modern **Vanilla CSS/JS** with a SaaS dashboard aesthetic.

---

## 🌟 Key Features

### 1. Two-Column Side-by-Side Dashboard Layout
- **Left Column**:
  - Welcome banner with student profile, registration number, university, and semester.
  - High-level metric cards: Total Subjects, Regular Attendance %, Medical Attendance %, Final Attendance %, and Eligibility Status.
  - Upcoming attendance warnings and critical shortage alerts.
  - Interactive **Subject-wise Attendance Table** with real-time colored indicators:
    - 🟢 **Safe** ($\ge 75\%$)
    - 🟡 **Warning** ($65\% - 74.9\%$)
    - 🔴 **Shortage** ($< 65\%$)
  - **Visual Analytics (Chart.js)**:
    - Subject-wise attendance breakdown (stacked bar chart).
    - Class distribution (attended vs medical approved vs missed doughnut chart).
    - Monthly attendance trends (line chart).
    - Regular vs Medical comparison chart.
- **Right Column (Dedicated Medical Attendance Panel)**:
  - **Subject-by-subject medical breakdown**:
    - Subject name and code
    - Number of approved medical classes
    - Medical attendance percentage contribution
  - **Aggregated medical metrics**:
    - Total medical classes approved
    - Overall medical attendance percentage boost
    - Total medically approved sick days
    - Pending medical applications counter
  - **Quick Action**: "Apply Medical Attendance" button with direct modal submission.
  - **Status Tracker**: Live status of submitted claims (`Pending`, `Approved`, `Rejected`) with admin remarks.

---

### 2. Medical Attendance Management (Core Feature)
- **Dedicated Medical Portal**: View and manage personal medical claims.
- **Secure Document Upload**: Upload doctor certificates and hospital discharge slips (`.pdf`, `.jpg`, `.png`).
- **Anti-Tamper Security**: In accordance with university cybersecurity standards, submitted and officially approved medical records cannot be altered by students without authorization.
- **Secure Document Viewer**: Integrated modal document preview preventing unauthorized file access.

---

### 3. Configurable Institutional Attendance Formulas
SmartAttend does **not** assume all institutions calculate attendance identically. Administrators can select from multiple statutory calculation modes in System Settings:

1. **Standard Addition Mode (Default)**:
   $$\text{Final \%} = \frac{\text{Attended Classes} + \text{Approved Medical Classes}}{\text{Total Classes Conducted}} \times 100$$
2. **Duty Leave / Exemption Subtraction Mode**:
   $$\text{Final \%} = \frac{\text{Attended Classes}}{\text{Total Classes Conducted} - \text{Approved Medical Classes}} \times 100$$
3. **Capped Benefit Mode**:
   $$\text{Final \%} = \text{Regular \%} + \min(\text{Medical \%}, \text{Max Benefit Cap})$$
4. **Weighted Factor Mode**:
   $$\text{Final \%} = \frac{\text{Attended Classes} + (\text{Approved Medical Classes} \times \text{Weight})}{\text{Total Classes Conducted}} \times 100$$

---

### 4. Smart Attendance Calculator & Recovery Predictor
- Instant interactive calculations **without page refresh**.
- Enter: Total conducted, attended, approved medical, upcoming planned classes, and target percentage slider ($60\% - 95\%$).
- Calculates:
  - Current regular attendance percentage.
  - Attendance after medical adjustments.
  - **Attendance Recovery Target**: Exact number of consecutive classes required to reach $75\%$ or any desired threshold.
  - **Safe Margin to Skip**: Maximum classes a student can miss without dropping below the target.
  - **Projection**: End-of-semester attendance after attending upcoming classes.
- Clickable preset buttons to load actual enrolled subjects directly into the calculator.

---

### 5. Official PDF & CSV Reports
- **Certified PDF Attendance Report**: Generated via ReportLab with student profile, overall metrics, subject-wise table with medical breakdown, institutional policy disclosure, and official signature blocks.
- **Master CSV Export**: Full university dataset export for administrative reporting.

---

### 6. Administration Command Center
- **Subject Management**: Add, update, and activate/deactivate courses.
- **Student Accounts**: Register students and auto-enroll them in semester subjects.
- **Verify Medical Certificates**: Authenticate uploaded medical slips, specify approved class counts, and add administrative verification notes.
- **Record Official Attendance**: Add or update recorded class attendance for any student.
- **System Configuration**: Adjust required attendance thresholds, warning thresholds, calculation formulas, and maximum medical days.
- **Security Audit Logs**: Chronological event trail tracking logins, file accesses, overrides, and security alerts.

---

### 7. Cybersecurity Architecture
- **Password Security**: State-of-the-art **Argon2id** password hashing.
- **Role-Based Access Control (RBAC)**: Strict separation between students and administrators.
- **IDOR Protection**: Secure file delivery endpoints verify user ownership before serving medical certificates.
- **CSRF Protection**: Form token validation across all mutations via Flask-WTF.
- **Brute-Force Rate Limiting**: Endpoint throttling via Flask-Limiter.
- **Input Sanitization**: File extension whitelisting, UUID renaming, and SQLAlchemy parameterized queries to prevent SQL Injection and XSS.
- **Security Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, and strict cache control.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Semantic HTML5, Vanilla CSS3 (Custom Properties & Design Tokens), Vanilla JavaScript (ES6+), Chart.js |
| **Backend** | Python 3.10+, Flask 3.1+, Flask-Login, Flask-WTF, Flask-Limiter |
| **Security** | Argon2-cffi (Argon2id), WTForms CSRF protection |
| **Database & ORM** | SQLAlchemy, SQLite (Default), PostgreSQL & MySQL support |
| **Document Engine** | ReportLab 5.1 (PDF Generation), Pillow (Image Processing) |

---

## 🚀 Quick Setup & Installation (VS Code)

### Step 1: Clone or Open the Project
Open the project directory in VS Code:
```bash
code "c:\Users\hp\OneDrive\Desktop\Attendance Management"
```

### Step 2: Install Dependencies
Ensure Python 3.10+ is installed, then install required packages:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy `.env.example` to `.env` (or use the provided `.env`):
```bash
cp .env.example .env
```

### Step 4: Initialize and Seed Sample Data
Run the database seeder to create subjects, sample students, realistic attendance records, and medical certificates:
```bash
python seed_data.py
```

### Step 5: Start the Development Server
Run the Flask server:
```bash
python run.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Credentials

The seeder provides pre-configured accounts:

### 🎓 Student Portal Demo
- **URL**: `http://127.0.0.1:5000/auth/login` (or click **"Student Demo"**)
- **Identity**: `alex.morgan@smartattend.edu` *(or roll number `RA2111003010042`)*
- **Password**: `Student@12345`
- **Features Demonstrated**: Side-by-side dashboard, approved and pending medical records, shortage warning on Computer Networks, live calculator recovery, and certified PDF export.

### 🛡️ Administrator Portal Demo
- **URL**: `http://127.0.0.1:5000/auth/login` (or click **"Admin Demo"**)
- **Identity**: `admin@smartattend.edu`
- **Password**: `Admin@12345`
- **Features Demonstrated**: Verification queue for pending certificate `MED-2026-0042`, attendance overrides, subject management, configurable formula settings, and security audit logs.

---

## 🗄️ Database Configuration (PostgreSQL / MySQL)

By default, the application runs friction-free on SQLite (`sqlite:///smartattend.db`). To connect to PostgreSQL or MySQL, update `DATABASE_URL` in `.env`:

### PostgreSQL:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/smartattend_db
```

### MySQL:
```env
DATABASE_URL=mysql+mysqlconnector://root:your_password@localhost:3306/smartattend_db
```

---

## 🧪 Running Automated Tests
Run the comprehensive unit and integration test suite:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📂 Project Directory Structure

```
Attendance Management/
├── app/
│   ├── __init__.py           # Application factory & security headers
│   ├── config.py             # Multi-environment configuration
│   ├── models/
│   │   ├── user.py           # User model with Argon2id hashing
│   │   ├── subject.py        # Course curriculum model
│   │   ├── attendance.py     # SubjectAttendance & session records
│   │   ├── medical.py        # MedicalApplication (anti-tamper locked)
│   │   ├── system_setting.py # Institutional formulas & thresholds
│   │   └── audit.py          # Security audit logs
│   ├── forms/                # Flask-WTF validation forms
│   ├── routes/               # Blueprints (auth, student, admin, api, files)
│   ├── services/             # Attendance engine, ReportLab PDF, and security
│   ├── static/
│   │   ├── css/              # variables.css, style.css, components.css
│   │   ├── js/               # main.js, charts.js, calculator.js, medical.js
│   │   └── img/              # SVG brand logo and default avatar
│   ├── templates/            # Jinja2 responsive templates
│   └── uploads/              # Protected storage for certificates & avatars
├── tests/                    # Automated unit and integration test suite
├── seed_data.py              # Sample dataset generator
├── run.py                    # Entry point runner
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # Complete documentation
```

---

## 📄 License
This project is licensed under the MIT License.
