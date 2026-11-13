from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.extensions import db
from app.models.feedback import Feedback
from app.models.patient import PatientProfile
from app.models.consultant import ConsultantProfile
from app.models.notification import Notification

feedback_bp = Blueprint("feedback", __name__, url_prefix="/api/feedback")

@feedback_bp.route("", methods=["GET"])
@jwt_required()
def get_feedbacks():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    if role == "patient":
        p = PatientProfile.query.filter_by(user_id=user_id).first()
        if not p:
            return jsonify({"error": "Patient not found"}), 404
        feedbacks = Feedback.query.filter_by(patient_id=p.id).order_by(Feedback.created_at.desc()).all()
    else:
        c = ConsultantProfile.query.filter_by(user_id=user_id).first()
        if not c:
            return jsonify({"error": "Consultant not found"}), 404
        patient_id = request.args.get("patient_id")
        if patient_id:
            feedbacks = Feedback.query.filter_by(consultant_id=c.id, patient_id=int(patient_id)).order_by(Feedback.created_at.desc()).all()
        else:
            feedbacks = Feedback.query.filter_by(consultant_id=c.id).order_by(Feedback.created_at.desc()).all()

    return jsonify([f.to_dict() for f in feedbacks]), 200

@feedback_bp.route("", methods=["POST"])
@jwt_required()
def create_feedback():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") != "consultant":
        return jsonify({"error": "Only consultants can send patient guidance notes"}), 403

    c = ConsultantProfile.query.filter_by(user_id=user_id).first()
    data = request.get_json() or {}
    patient_id = data.get("patient_id")
    message = (data.get("message") or "").strip()

    if not patient_id or not message:
        return jsonify({"error": "patient_id and message are required"}), 400

    p = PatientProfile.query.get(int(patient_id))
    if not p:
        return jsonify({"error": "Patient not found"}), 404

    feedback = Feedback(
        consultant_id=c.id,
        patient_id=p.id,
        message=message
    )
    db.session.add(feedback)

    notif = Notification(
        user_id=p.user_id,
        title=f"Clinical Note from {c.full_name}",
        message=message,
        notif_type="consultant_feedback"
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({
        "message": "Feedback sent successfully",
        "feedback": feedback.to_dict()
    }), 201

@feedback_bp.route("/<int:feedback_id>/read", methods=["PUT"])
@jwt_required()
def mark_read(feedback_id):
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
        return jsonify({"error": "Feedback not found"}), 404
    feedback.is_read = True
    db.session.commit()
    return jsonify({"message": "Feedback marked as read"}), 200
