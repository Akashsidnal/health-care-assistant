from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule
from app.models.dose import DoseRecord
from app.models.feedback import Feedback
from app.models.notification import Notification
from app.services.adherence_service import AdherenceService
from app.utils.decorators import patient_required

patient_bp = Blueprint("patient", __name__, url_prefix="/api/patient")

def _get_current_patient():
    user_id = int(get_jwt_identity())
    return PatientProfile.query.filter_by(user_id=user_id).first()

@patient_bp.route("/profile", methods=["GET"])
@patient_required
def get_profile():
    patient = _get_current_patient()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404
    return jsonify(patient.to_dict()), 200

@patient_bp.route("/profile", methods=["PUT"])
@patient_required
def update_profile():
    patient = _get_current_patient()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    data = request.get_json() or {}
    for field in ["full_name", "phone_number", "age", "gender", "disease_condition", "address", "emergency_contact"]:
        if field in data:
            setattr(patient, field, data[field])

    db.session.commit()
    return jsonify({
        "message": "Profile updated successfully",
        "profile": patient.to_dict()
    }), 200

@patient_bp.route("/dashboard", methods=["GET"])
@patient_required
def get_dashboard():
    patient = _get_current_patient()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    # Evaluate past pending doses for auto-miss
    AdherenceService.auto_mark_missed_doses(patient.id)

    # Adherence metrics
    adherence_data = AdherenceService.get_patient_adherence_summary(patient.id)
    
    # Ensure today's scheduled dose records exist in database
    active_schedules = MedicineSchedule.query.join(Medicine).filter(
        Medicine.patient_id == patient.id,
        Medicine.is_active == True,
        MedicineSchedule.is_active == True
    ).all()

    for s in active_schedules:
        sched_time_full = f"{today_str} {s.scheduled_time}"
        existing = DoseRecord.query.filter_by(
            patient_id=patient.id,
            schedule_id=s.id,
            scheduled_time=sched_time_full
        ).first()
        if not existing:
            new_dose = DoseRecord(
                patient_id=patient.id,
                medicine_id=s.medicine_id,
                schedule_id=s.id,
                scheduled_time=sched_time_full,
                status="PENDING"
            )
            db.session.add(new_dose)
    db.session.commit()

    # Re-fetch today's doses
    today_doses = DoseRecord.query.filter(
        DoseRecord.patient_id == patient.id,
        DoseRecord.scheduled_time.startswith(today_str)
    ).order_by(DoseRecord.scheduled_time.asc()).all()

    # Find next pending dose
    now_time_str = now.strftime("%Y-%m-%d %H:%M")
    next_dose = None
    for d in today_doses:
        if d.status == "PENDING" and d.scheduled_time >= now_time_str:
            next_dose = d.to_dict()
            break

    # Recent doctor feedback
    feedbacks = Feedback.query.filter_by(patient_id=patient.id).order_by(Feedback.created_at.desc()).limit(5).all()
    notifications = Notification.query.filter_by(user_id=patient.user_id, is_read=False).order_by(Notification.created_at.desc()).all()

    return jsonify({
        "welcome_message": f"Welcome back, {patient.full_name}",
        "today_date": now.strftime("%A, %B %d, %Y"),
        "today_stats": adherence_data["today"],
        "adherence": adherence_data,
        "next_medicine": next_dose,
        "today_doses": [d.to_dict() for d in today_doses],
        "consultant": patient.consultant.to_dict() if patient.consultant else None,
        "emergency_contact": patient.emergency_contact,
        "feedbacks": [f.to_dict() for f in feedbacks],
        "unread_notifications": len(notifications)
    }), 200

@patient_bp.route("/calendar", methods=["GET"])
@patient_required
def get_calendar():
    patient = _get_current_patient()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    now = datetime.now()
    year = int(request.args.get("year", now.year))
    month = int(request.args.get("month", now.month))

    data = AdherenceService.get_month_calendar_data(patient.id, year, month)
    return jsonify(data), 200
