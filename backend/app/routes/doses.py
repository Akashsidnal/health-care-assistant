from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models.dose import DoseRecord
from app.models.patient import PatientProfile
from app.models.schedule import MedicineSchedule
from app.services.adherence_service import AdherenceService

doses_bp = Blueprint("doses", __name__, url_prefix="/api/doses")

def _get_patient_id():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") == "patient":
        p = PatientProfile.query.filter_by(user_id=user_id).first()
        return p.id if p else None
    return None

@doses_bp.route("", methods=["GET"])
@jwt_required()
def get_doses():
    patient_id = _get_patient_id() or request.args.get("patient_id")
    if not patient_id:
        return jsonify({"error": "Patient ID is required"}), 400

    AdherenceService.auto_mark_missed_doses(int(patient_id))
    query = DoseRecord.query.filter_by(patient_id=int(patient_id))

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status.upper())

    date = request.args.get("date")
    if date:
        query = query.filter(DoseRecord.scheduled_time.startswith(date))

    doses = query.order_by(DoseRecord.scheduled_time.desc()).all()
    return jsonify([d.to_dict() for d in doses]), 200

@doses_bp.route("/record", methods=["POST"])
@jwt_required()
def record_dose():
    patient_id = _get_patient_id()
    data = request.get_json() or {}

    if not patient_id:
        patient_id = data.get("patient_id")

    schedule_id = data.get("schedule_id")
    scheduled_time = data.get("scheduled_time")
    status = (data.get("status") or "TAKEN").upper()
    actual_time = data.get("actual_time") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notes = data.get("notes")

    if not schedule_id or not scheduled_time:
        return jsonify({"error": "schedule_id and scheduled_time are required"}), 400

    if status not in ["PENDING", "TAKEN", "SKIPPED", "MISSED"]:
        return jsonify({"error": "Status must be PENDING, TAKEN, SKIPPED, or MISSED"}), 400

    schedule = MedicineSchedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404

    existing = DoseRecord.query.filter_by(
        patient_id=patient_id,
        schedule_id=schedule_id,
        scheduled_time=scheduled_time
    ).first()

    if existing:
        existing.status = status
        existing.actual_time = actual_time
        if notes:
            existing.notes = notes
        db.session.commit()
        return jsonify({
            "message": f"Dose status updated to {status}",
            "dose": existing.to_dict()
        }), 200

    dose = DoseRecord(
        patient_id=patient_id,
        medicine_id=schedule.medicine_id,
        schedule_id=schedule_id,
        scheduled_time=scheduled_time,
        actual_time=actual_time,
        status=status,
        notes=notes
    )
    db.session.add(dose)
    db.session.commit()

    return jsonify({
        "message": f"Dose recorded as {status}",
        "dose": dose.to_dict()
    }), 201

@doses_bp.route("/<int:dose_id>/action", methods=["POST"])
@jwt_required()
def perform_action(dose_id):
    dose = DoseRecord.query.get(dose_id)
    if not dose:
        return jsonify({"error": "Dose record not found"}), 404

    data = request.get_json() or {}
    action = (data.get("status") or "TAKEN").upper()
    
    if action not in ["TAKEN", "SKIPPED", "MISSED"]:
        return jsonify({"error": "Invalid action status"}), 400

    dose.status = action
    dose.actual_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if data.get("notes"):
        dose.notes = data["notes"]
        
    db.session.commit()
    return jsonify({
        "message": f"Dose marked as {action}",
        "dose": dose.to_dict()
    }), 200
