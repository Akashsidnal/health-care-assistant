from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.patient import PatientProfile
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule
from app.models.dose import DoseRecord
from app.models.feedback import Feedback
from app.models.notification import Notification

sync_bp = Blueprint("sync", __name__, url_prefix="/api/sync")

@sync_bp.route("/batch", methods=["POST"])
@jwt_required()
def batch_sync():
    user_id = int(get_jwt_identity())
    patient = PatientProfile.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({"error": "Patient profile not found"}), 404

    data = request.get_json() or {}
    server_time = datetime.now(timezone.utc).isoformat()
    synced_doses_count = 0

    client_doses = data.get("dose_records", [])
    for dose_item in client_doses:
        schedule_id = dose_item.get("schedule_id")
        scheduled_time = dose_item.get("scheduled_time")
        status = (dose_item.get("status") or "TAKEN").upper()
        actual_time = dose_item.get("actual_time")
        notes = dose_item.get("notes")

        if not schedule_id or not scheduled_time:
            continue

        schedule = MedicineSchedule.query.get(schedule_id)
        if not schedule:
            continue

        existing = DoseRecord.query.filter_by(
            patient_id=patient.id,
            schedule_id=schedule_id,
            scheduled_time=scheduled_time
        ).first()

        if existing:
            if existing.status != status:
                existing.status = status
                existing.actual_time = actual_time or server_time
                if notes:
                    existing.notes = notes
                synced_doses_count += 1
        else:
            new_dose = DoseRecord(
                patient_id=patient.id,
                medicine_id=schedule.medicine_id,
                schedule_id=schedule_id,
                scheduled_time=scheduled_time,
                actual_time=actual_time or server_time,
                status=status,
                notes=notes
            )
            db.session.add(new_dose)
            synced_doses_count += 1

    db.session.commit()

    active_medicines = Medicine.query.filter_by(patient_id=patient.id, is_active=True).all()
    all_schedules = MedicineSchedule.query.join(Medicine).filter(
        Medicine.patient_id == patient.id,
        Medicine.is_active == True,
        MedicineSchedule.is_active == True
    ).all()

    feedbacks = Feedback.query.filter_by(patient_id=patient.id).order_by(Feedback.created_at.desc()).limit(15).all()
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc()).all()

    return jsonify({
        "status": "success",
        "synced_doses_count": synced_doses_count,
        "server_timestamp": server_time,
        "payload": {
            "patient": patient.to_dict(),
            "medicines": [m.to_dict(include_schedules=False) for m in active_medicines],
            "schedules": [s.to_dict() for s in all_schedules],
            "feedbacks": [f.to_dict() for f in feedbacks],
            "notifications": [n.to_dict() for n in notifications]
        }
    }), 200
