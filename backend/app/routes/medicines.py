from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models.patient import PatientProfile
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule
from app.utils.security import save_uploaded_file

medicines_bp = Blueprint("medicines", __name__, url_prefix="/api/medicines")

def _get_patient():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") == "patient":
        return PatientProfile.query.filter_by(user_id=user_id).first()
    return None

@medicines_bp.route("", methods=["GET"])
@jwt_required()
def get_medicines():
    patient = _get_patient()
    if not patient:
        patient_id = request.args.get("patient_id")
        if patient_id:
            patient = PatientProfile.query.get(int(patient_id))
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

    meds = Medicine.query.filter_by(patient_id=patient.id).all()
    return jsonify([m.to_dict() for m in meds]), 200

@medicines_bp.route("", methods=["POST"])
@jwt_required()
def create_medicine():
    patient = _get_patient()
    data = request.form if request.form else (request.get_json() or {})
    
    if not patient:
        patient_id = data.get("patient_id")
        if patient_id:
            patient = PatientProfile.query.get(int(patient_id))
        if not patient:
            return jsonify({"error": "Target patient not identified"}), 400

    name = data.get("name")
    dosage = data.get("dosage")
    if not name or not dosage:
        return jsonify({"error": "Medicine name and dosage are required"}), 400

    photo_filename = None
    prescription_doc = None

    if "photo" in request.files:
        try:
            photo_filename = save_uploaded_file(request.files["photo"], prefix="pill")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if "prescription" in request.files:
        try:
            prescription_doc = save_uploaded_file(request.files["prescription"], prefix="rx")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    med = Medicine(
        patient_id=patient.id,
        name=name.strip(),
        photo_filename=photo_filename,
        prescription_doc=prescription_doc,
        dosage=dosage.strip(),
        tablet_count=int(data.get("tablet_count", 30)),
        frequency=data.get("frequency", "Once daily"),
        instructions=data.get("instructions", ""),
        notes=data.get("notes", ""),
        is_active=True
    )
    db.session.add(med)
    db.session.flush()

    times_input = data.get("times") or data.get("scheduled_time") or "08:00"
    if isinstance(times_input, list):
        times = times_input
    else:
        times = [t.strip() for t in str(times_input).split(",") if t.strip()]

    start_date = data.get("start_date", "2026-01-01")
    for t in times:
        sched = MedicineSchedule(
            medicine_id=med.id,
            scheduled_time=t,
            start_date=start_date,
            days_of_week=data.get("days_of_week", "EVERY_DAY")
        )
        db.session.add(sched)

    db.session.commit()
    return jsonify({
        "message": "Prescription recorded successfully",
        "medicine": med.to_dict()
    }), 201

@medicines_bp.route("/<int:medicine_id>/pause", methods=["POST"])
@jwt_required()
def pause_medicine(medicine_id):
    med = Medicine.query.get(medicine_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404
    med.is_active = False
    db.session.commit()
    return jsonify({"message": f"Medicine '{med.name}' paused", "is_active": False}), 200

@medicines_bp.route("/<int:medicine_id>/resume", methods=["POST"])
@jwt_required()
def resume_medicine(medicine_id):
    med = Medicine.query.get(medicine_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404
    med.is_active = True
    db.session.commit()
    return jsonify({"message": f"Medicine '{med.name}' resumed", "is_active": True}), 200

@medicines_bp.route("/<int:medicine_id>", methods=["DELETE"])
@jwt_required()
def delete_medicine(medicine_id):
    med = Medicine.query.get(medicine_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404
    db.session.delete(med)
    db.session.commit()
    return jsonify({"message": "Medicine removed"}), 200
