import unittest
import json
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.consultant import ConsultantProfile
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule
from app.models.dose import DoseRecord
from app.services.adherence_service import AdherenceService

class MediCareApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("host_ip", data)

    def test_02_register_and_login_doctor(self):
        # Register Consultant
        res = self.client.post("/api/auth/register", json={
            "email": "dr.test@smarthealth.demo",
            "password": "Password@123",
            "role": "consultant",
            "full_name": "Dr. Tester",
            "specialization": "Cardiology",
            "clinic_name": "City Heart Center"
        })
        self.assertEqual(res.status_code, 201)

        # Login
        res = self.client.post("/api/auth/login", json={
            "email": "dr.test@smarthealth.demo",
            "password": "Password@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["role"], "consultant")

    def test_03_register_and_login_patient(self):
        # Register Patient
        res = self.client.post("/api/auth/register", json={
            "email": "patient.test@smarthealth.demo",
            "password": "Password@123",
            "role": "patient",
            "full_name": "Test Patient",
            "age": 45,
            "disease_condition": "Hypertension",
            "phone_number": "9876543210"
        })
        self.assertEqual(res.status_code, 201)

        # Login
        res = self.client.post("/api/auth/login", json={
            "email": "patient.test@smarthealth.demo",
            "password": "Password@123"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("token", data)
        self.assertEqual(data["user"]["role"], "patient")

    def test_04_adherence_formula(self):
        with self.app.app_context():
            u = User.query.filter_by(email="patient.test@smarthealth.demo").first()
            p = u.patient_profile

            med = Medicine(patient_id=p.id, name="Amlodipine 5mg", dosage="1 Tab")
            db.session.add(med)
            db.session.commit()

            # Add 3 TAKEN, 1 SKIPPED, 1 MISSED -> Adherence = 3 / (3 + 1 + 1) * 100 = 60.0%
            d1 = DoseRecord(patient_id=p.id, medicine_id=med.id, scheduled_time="2026-03-01 08:00", status="TAKEN")
            d2 = DoseRecord(patient_id=p.id, medicine_id=med.id, scheduled_time="2026-03-02 08:00", status="TAKEN")
            d3 = DoseRecord(patient_id=p.id, medicine_id=med.id, scheduled_time="2026-03-03 08:00", status="TAKEN")
            d4 = DoseRecord(patient_id=p.id, medicine_id=med.id, scheduled_time="2026-03-04 08:00", status="SKIPPED")
            d5 = DoseRecord(patient_id=p.id, medicine_id=med.id, scheduled_time="2026-03-05 08:00", status="MISSED")
            db.session.add_all([d1, d2, d3, d4, d5])
            db.session.commit()

            stats = AdherenceService.calculate_adherence(p.id)
            self.assertEqual(stats["taken"], 3)
            self.assertEqual(stats["skipped"], 1)
            self.assertEqual(stats["missed"], 1)
            self.assertEqual(stats["percentage"], 60.0)

    def test_05_dose_actions_and_feedback(self):
        # Login doctor
        res = self.client.post("/api/auth/login", json={
            "email": "dr.test@smarthealth.demo",
            "password": "Password@123"
        })
        doc_token = res.get_json()["token"]

        # Login patient
        res = self.client.post("/api/auth/login", json={
            "email": "patient.test@smarthealth.demo",
            "password": "Password@123"
        })
        pat_token = res.get_json()["token"]

        with self.app.app_context():
            u = User.query.filter_by(email="patient.test@smarthealth.demo").first()
            pat_id = u.patient_profile.id

        # Send Doctor Feedback
        res = self.client.post("/api/feedback", headers={"Authorization": f"Bearer {doc_token}"}, json={
            "patient_id": pat_id,
            "message": "Take blood pressure medication before breakfast."
        })
        self.assertEqual(res.status_code, 201)

        # Get feedback as patient
        res = self.client.get("/api/feedback", headers={"Authorization": f"Bearer {pat_token}"})
        self.assertEqual(res.status_code, 200)
        feedbacks = res.get_json()
        self.assertGreaterEqual(len(feedbacks), 1)

    def test_06_reports_export(self):
        res = self.client.post("/api/auth/login", json={
            "email": "dr.test@smarthealth.demo",
            "password": "Password@123"
        })
        doc_token = res.get_json()["token"]

        with self.app.app_context():
            u = User.query.filter_by(email="patient.test@smarthealth.demo").first()
            pat_id = u.patient_profile.id

        res = self.client.get(f"/api/reports/csv?patient_id={pat_id}", headers={"Authorization": f"Bearer {doc_token}"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.headers.get("Content-Type", ""))
        self.assertIn("MEDICARE CLOUD ADHERENCE REPORT", res.data.decode("utf-8"))

if __name__ == "__main__":
    unittest.main()
