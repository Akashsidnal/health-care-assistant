from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.consultant import ConsultantProfile
from app.models.medicine import Medicine
from app.models.dose import DoseRecord
from app.models.feedback import Feedback
from app.services.adherence_service import AdherenceService
from app.utils.decorators import consultant_required

consultant_bp = Blueprint("consultant", __name__, url_prefix="/api/consultant")

def _get_consultant():
    user_id = int(get_jwt_identity())
    return ConsultantProfile.query.filter_by(user_id=user_id).first()

@consultant_bp.route("/dashboard", methods=["GET"])
@consultant_required
def get_dashboard_stats():
    consultant = _get_consultant()
    if not consultant:
        return jsonify({"error": "Consultant profile not found"}), 404

    patients = consultant.patients.all()
    total_patients = len(patients)

    patients_needing_attention = 0
    today_missed_total = 0
    total_adherence_sum = 0.0
    recent_activities = []

    for p in patients:
        stats = AdherenceService.get_patient_adherence_summary(p.id)
        overall_pct = stats["overall"]["percentage"]
        total_adherence_sum += overall_pct
        
        today_missed = stats["today"]["missed"]
        today_missed_total += today_missed

        if overall_pct < 70.0 or today_missed > 0:
            patients_needing_attention += 1

    overall_avg_adherence = round(total_adherence_sum / total_patients, 1) if total_patients > 0 else 100.0

    patient_ids = [p.id for p in patients]
    if patient_ids:
        recent_doses = DoseRecord.query.filter(
            DoseRecord.patient_id.in_(patient_ids),
            DoseRecord.status.in_(["TAKEN", "SKIPPED", "MISSED"])
        ).order_by(DoseRecord.updated_at.desc()).limit(8).all()
        
        for d in recent_doses:
            recent_activities.append({
                "patient_name": d.patient.full_name,
                "medicine_name": d.medicine.name,
                "status": d.status,
                "time": d.actual_time or d.scheduled_time,
                "patient_id": d.patient_id
            })

    return jsonify({
        "total_patients": total_patients,
        "patients_needing_attention": patients_needing_attention,
        "today_missed_doses": today_missed_total,
        "overall_adherence": overall_avg_adherence,
        "recent_activities": recent_activities
    }), 200

@consultant_bp.route("/patients", methods=["GET"])
@consultant_required
def get_patients():
    consultant = _get_consultant()
    if not consultant:
        return jsonify({"error": "Consultant profile not found"}), 404

    search_query = request.args.get("search", "").strip().lower()
    filter_type = request.args.get("filter", "all").strip().lower()

    patients = consultant.patients.all()
    patient_list = []

    for p in patients:
        if search_query:
            if search_query not in p.full_name.lower() and search_query not in p.phone_number.lower():
                continue

        stats = AdherenceService.get_patient_adherence_summary(p.id)
        overall_pct = stats["overall"]["percentage"]
        today_missed = stats["today"]["missed"]
        today_taken = stats["today"]["taken"]
        today_skipped = stats["today"]["skipped"]
        today_pending = stats["today"]["pending"]

        if filter_type == "high" and overall_pct < 80.0:
            continue
        if filter_type == "low" and overall_pct >= 70.0:
            continue
        if filter_type == "missed" and today_missed == 0:
            continue

        active_meds = p.medicines.filter_by(is_active=True).count()

        patient_list.append({
            "id": p.id,
            "full_name": p.full_name,
            "age": p.age,
            "gender": p.gender,
            "phone_number": p.phone_number,
            "disease_condition": p.disease_condition,
            "active_medicines_count": active_meds,
            "adherence_percentage": overall_pct,
            "today_status": {
                "taken": today_taken,
                "skipped": today_skipped,
                "missed": today_missed,
                "pending": today_pending
            }
        })

    return jsonify(patient_list), 200

@consultant_bp.route("/patients/<int:patient_id>", methods=["GET"])
@consultant_required
def get_patient_detail(patient_id):
    consultant = _get_consultant()
    patient = PatientProfile.query.get(patient_id)
    
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    if patient.consultant_id != consultant.id:
        return jsonify({"error": "Unauthorized access to patient outside your care"}), 403

    medicines = [m.to_dict() for m in patient.medicines.all()]
    adherence_summary = AdherenceService.get_patient_adherence_summary(patient.id)
    recent_feedbacks = [f.to_dict() for f in patient.feedbacks.order_by(Feedback.created_at.desc()).limit(10).all()]

    return jsonify({
        "patient": patient.to_dict(),
        "medicines": medicines,
        "adherence": adherence_summary,
        "feedbacks": recent_feedbacks
    }), 200

@consultant_bp.route("/patients/assign", methods=["POST"])
@consultant_required
def assign_patient():
    consultant = _get_consultant()
    data = request.get_json() or {}
    patient_email = data.get("email")

    if not patient_email:
        return jsonify({"error": "Patient email is required"}), 400

    user = User.query.filter_by(email=patient_email.strip().lower(), role="patient").first()
    patient = user.patient_profile if user else None

    if not patient:
        return jsonify({"error": "No registered patient found with this email"}), 404

    patient.consultant_id = consultant.id
    db.session.commit()

    return jsonify({
        "message": f"Patient {patient.full_name} added to your care roster",
        "patient": patient.to_dict()
    }), 200
