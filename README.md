# MediCare Cloud: Smart Healthcare Monitoring & Medication Reminder System Using Cloud Technology

An enterprise-grade, cloud-enabled healthcare monitoring and medication adherence tracking platform developed for patients and medical consultants.

---

## Academic Information & Attribution
- **Institution:** City Engineering College, Bengaluru – 560061
- **Department:** Department of Information Science and Engineering (ISE)
- **Academic Year:** 2026 – 2027
- **Project Guide:** Mrs. Hemalatha D, Associate Professor, Dept. of ISE
- **Student Team:**
  - **Akash N Sidnal** (USN: `1CE23IS008`)
  - **Bhartesh P B** (USN: `1CE23IS016`)
  - **Chethan V** (USN: `1CE23IS025`)
  - **Likith I N** (USN: `1CE23IS047`)

---

## Key Modules & System Architecture

### 1. Patient Portal & Real-Time Reminders
- **Dual-Mode Audio Alarms:** Web Audio API alarm synthesized locally with visual modal pulse and browser notifications.
- **Three-State Compliance Tracking:** Distinguishes between:
  - `TAKEN`: Patient confirmed medication intake.
  - `SKIPPED`: Intentional patient action (e.g., fasting, medical advice).
  - `MISSED`: Unacknowledged dose after the configurable grace period (30 minutes).
- **Interactive Adherence Calendar:** Visual month matrix with green, yellow, and red status indicators for daily compliance audits.
- **Digital Prescription Locker:** Storage and retrieval for digital prescriptions and pill reference photos.

### 2. Consultant / Physician Clinical Roster
- **Clinical Dashboard:** Patient cohort metrics, at-risk patient identification ($\text{Adherence} < 70\%$), and real-time dose stream.
- **Patient Management:** Detailed health profiles, dosage adjustments, and pause/resume prescription controls.
- **Clinical Guidance Channel:** Real-time dietary precautions, dosage instructions, and check-in notes delivered straight to the patient.
- **Official Compliance Audits:** Print-ready reports and CSV export for clinical reviews.

### 3. Multi-Device LAN & Mobile Architecture
- **Flask RESTful Backend:** Accessible across the entire local area network (`0.0.0.0:5000`).
- **Progressive Web App (PWA):** Zero-install home screen execution with offline caching.
- **Native Android APK Wrapper:** Standalone Android project ready for compilation in Android Studio.

---

## 1-Click Execution

To launch the entire platform, double-click:
```
START_MEDICARE_CLOUD.bat
```
*(Also available on your Windows Desktop).*

### Manual Terminal Launch
```powershell
cd "C:\Users\AKASH N SIDNAL\MediCareCloud\backend"
python seed_data.py
python run.py
```

### Access URLs
- **Local Machine:** `http://127.0.0.1:5000`
- **Smartphones / Tablets on Same Wi-Fi:** `http://192.168.0.102:5000` (auto-detected on launch)

### Pre-Configured Test Credentials (1-Click Autofill on Login Page)
| Role | Email | Password |
|---|---|---|
| **Medical Consultant** | `doctor@smarthealth.demo` | `password123` *(or `Doctor@123`)* |
| **Enrolled Patient** | `patient@smarthealth.demo` | `password123` *(or `Patient@123`)* |
| **Secondary Patient (At-Risk)** | `mary@smarthealth.demo` | `password123` *(or `Patient@123`)* |
