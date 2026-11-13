from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.patient import PatientProfile
from app.services.adherence_service import AdherenceService

adherence_bp = Blueprint("adherence", __name__, url_prefix="/api/adherence")

@adherence_bp.route("", methods=["GET"])
@jwt_required()
def get_adherence():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    patient_id = request.args.get("patient_id")
    if not patient_id:
        if claims.get("role") == "patient":
            p = PatientProfile.query.filter_by(user_id=user_id).first()
            if p:
                patient_id = p.id
    else:
        patient_id = int(patient_id)

    if not patient_id:
        return jsonify({"error": "Patient ID could not be identified"}), 400

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    medicine_id = request.args.get("medicine_id")

    if start_date or end_date or medicine_id:
        stats = AdherenceService.calculate_adherence(
            patient_id=patient_id,
            start_dt_str=start_date,
            end_dt_str=end_date,
            medicine_id=int(medicine_id) if medicine_id else None
        )
        return jsonify(stats), 200

    summary = AdherenceService.get_patient_adherence_summary(patient_id)
    return jsonify(summary), 200
