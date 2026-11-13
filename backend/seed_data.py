from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.consultant import ConsultantProfile
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule
from app.models.dose import DoseRecord
from app.models.feedback import Feedback
from app.models.notification import Notification

def seed_database():
    print("[Seed] Initializing MediCare Cloud Database...")

    if User.query.filter_by(email="doctor@smarthealth.demo").first():
        print("[Seed] Preloaded dataset already present.")
        return

    # 1. Consultant
    c_user = User(email="doctor@smarthealth.demo", role="consultant")
    c_user.set_password("password123")
    db.session.add(c_user)
    db.session.flush()

    consultant = ConsultantProfile(
        user_id=c_user.id,
        full_name="Dr. Sarah Jenkins, MD",
        phone_number="+1-555-019-2834",
        designation="Senior Consultant Physician & Diabetologist",
        specialization="Endocrinology & Chronic Care",
        organization="City Memorial Healthcare"
    )
    db.session.add(consultant)
    db.session.flush()

    # 2. Patient 1: Robert Miller (Good Adherence ~88%)
    p1_user = User(email="patient@smarthealth.demo", role="patient")
    p1_user.set_password("password123")
    db.session.add(p1_user)
    db.session.flush()

    p1 = PatientProfile(
        user_id=p1_user.id,
        full_name="Robert Miller",
        phone_number="+1-555-014-9982",
        age=68,
        gender="Male",
        disease_condition="Type 2 Diabetes & Hypertension",
        address="742 Evergreen Terrace, Bengaluru",
        emergency_contact="Emily Miller (Daughter) - +1-555-014-9983",
        consultant_id=consultant.id
    )
    db.session.add(p1)
    db.session.flush()

    med1 = Medicine(
        patient_id=p1.id, name="Metformin", dosage="500 mg (1 tablet)",
        tablet_count=45, frequency="Twice daily", instructions="Take with meals",
        notes="Blood sugar management", is_active=True
    )
    med2 = Medicine(
        patient_id=p1.id, name="Lisinopril", dosage="10 mg (1 tablet)",
        tablet_count=28, frequency="Once daily", instructions="Take in morning with water",
        notes="Blood pressure management", is_active=True
    )
    med3 = Medicine(
        patient_id=p1.id, name="Atorvastatin", dosage="20 mg (1 tablet)",
        tablet_count=30, frequency="Once daily at bedtime", instructions="Take at night",
        notes="Cholesterol control", is_active=True
    )
    db.session.add_all([med1, med2, med3])
    db.session.flush()

    sched1_am = MedicineSchedule(medicine_id=med1.id, scheduled_time="08:00", start_date="2026-10-01")
    sched1_pm = MedicineSchedule(medicine_id=med1.id, scheduled_time="20:00", start_date="2026-10-01")
    sched2_am = MedicineSchedule(medicine_id=med2.id, scheduled_time="09:00", start_date="2026-10-01")
    sched3_pm = MedicineSchedule(medicine_id=med3.id, scheduled_time="21:00", start_date="2026-10-01")
    db.session.add_all([sched1_am, sched1_pm, sched2_am, sched3_pm])
    db.session.flush()

    now = datetime.now()
    # Past 7 days history for Patient 1
    for i in range(7, 0, -1):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Metformin AM - TAKEN
        db.session.add(DoseRecord(
            patient_id=p1.id, medicine_id=med1.id, schedule_id=sched1_am.id,
            scheduled_time=f"{day} 08:00", actual_time=f"{day} 08:04:12", status="TAKEN"
        ))
        # Lisinopril AM - TAKEN
        db.session.add(DoseRecord(
            patient_id=p1.id, medicine_id=med2.id, schedule_id=sched2_am.id,
            scheduled_time=f"{day} 09:00", actual_time=f"{day} 09:02:15", status="TAKEN"
        ))
        # Metformin PM - Skipped on day 3 with note
        status_pm = "SKIPPED" if i == 3 else "TAKEN"
        notes_pm = "Felt mild stomach upset after dinner" if i == 3 else None
        db.session.add(DoseRecord(
            patient_id=p1.id, medicine_id=med1.id, schedule_id=sched1_pm.id,
            scheduled_time=f"{day} 20:00", actual_time=f"{day} 20:05:00", status=status_pm, notes=notes_pm
        ))
        # Atorvastatin PM - TAKEN
        db.session.add(DoseRecord(
            patient_id=p1.id, medicine_id=med3.id, schedule_id=sched3_pm.id,
            scheduled_time=f"{day} 21:00", actual_time=f"{day} 21:01:00", status="TAKEN"
        ))

    # Today's dose for Patient 1
    today_str = now.strftime("%Y-%m-%d")
    db.session.add(DoseRecord(
        patient_id=p1.id, medicine_id=med1.id, schedule_id=sched1_am.id,
        scheduled_time=f"{today_str} 08:00", actual_time=f"{today_str} 08:03:00", status="TAKEN"
    ))
    db.session.add(DoseRecord(
        patient_id=p1.id, medicine_id=med2.id, schedule_id=sched2_am.id,
        scheduled_time=f"{today_str} 09:00", actual_time=f"{today_str} 09:01:40", status="TAKEN"
    ))
    db.session.add(DoseRecord(
        patient_id=p1.id, medicine_id=med1.id, schedule_id=sched1_pm.id,
        scheduled_time=f"{today_str} 20:00", status="PENDING"
    ))
    db.session.add(DoseRecord(
        patient_id=p1.id, medicine_id=med3.id, schedule_id=sched3_pm.id,
        scheduled_time=f"{today_str} 21:00", status="PENDING"
    ))

    # Doctor feedback for Patient 1
    db.session.add(Feedback(
        consultant_id=consultant.id, patient_id=p1.id,
        message="Robert, your adherence on Lisinopril and Metformin has been very consistent. Keep up the morning routine!",
        is_read=True
    ))

    # 3. Patient 2: Mary Watson (Needs Attention, Adherence ~55%)
    p2_user = User(email="mary@smarthealth.demo", role="patient")
    p2_user.set_password("password123")
    db.session.add(p2_user)
    db.session.flush()

    p2 = PatientProfile(
        user_id=p2_user.id, full_name="Mary Watson",
        phone_number="+1-555-018-7744", age=73, gender="Female",
        disease_condition="Cardiac Arrhythmia & Osteoarthritis",
        address="104 Baker Street, Bengaluru",
        emergency_contact="John Watson (Son) - +1-555-018-7745",
        consultant_id=consultant.id
    )
    db.session.add(p2)
    db.session.flush()

    med_p2 = Medicine(
        patient_id=p2.id, name="Metoprolol Succinate", dosage="25 mg (1 tablet)",
        tablet_count=20, frequency="Twice daily", instructions="Swallow whole with water",
        notes="Heart rate control", is_active=True
    )
    db.session.add(med_p2)
    db.session.flush()

    sched_p2_am = MedicineSchedule(medicine_id=med_p2.id, scheduled_time="08:00", start_date="2026-10-01")
    sched_p2_pm = MedicineSchedule(medicine_id=med_p2.id, scheduled_time="18:00", start_date="2026-10-01")
    db.session.add_all([sched_p2_am, sched_p2_pm])
    db.session.flush()

    for i in range(5, 0, -1):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        status_am = "MISSED" if i in [1, 3, 5] else "TAKEN"
        status_pm = "SKIPPED" if i in [2, 4] else "TAKEN"
        db.session.add(DoseRecord(
            patient_id=p2.id, medicine_id=med_p2.id, schedule_id=sched_p2_am.id,
            scheduled_time=f"{day} 08:00", status=status_am,
            notes="No response within reminder window" if status_am == "MISSED" else None
        ))
        db.session.add(DoseRecord(
            patient_id=p2.id, medicine_id=med_p2.id, schedule_id=sched_p2_pm.id,
            scheduled_time=f"{day} 18:00", status=status_pm,
            notes="Patient chose to skip dose" if status_pm == "SKIPPED" else None
        ))

    db.session.add(DoseRecord(
        patient_id=p2.id, medicine_id=med_p2.id, schedule_id=sched_p2_am.id,
        scheduled_time=f"{today_str} 08:00", status="MISSED",
        notes="Morning dose timed out"
    ))
    db.session.add(DoseRecord(
        patient_id=p2.id, medicine_id=med_p2.id, schedule_id=sched_p2_pm.id,
        scheduled_time=f"{today_str} 18:00", status="PENDING"
    ))

    db.session.commit()
    print("[Seed] Preloaded dataset initialized successfully!")

if __name__ == "__main__":
    app = create_app("development")
    with app.app_context():
        db.create_all()
        seed_database()
