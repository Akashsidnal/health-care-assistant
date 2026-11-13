from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.patient import PatientProfile
from app.models.consultant import ConsultantProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password")
    role = (data.get("role") or "patient").strip().lower()
    full_name = (data.get("full_name") or "").strip()
    phone_number = (data.get("phone_number") or "").strip() or "N/A"

    if not email or not password or not full_name:
        return jsonify({"error": "Email, password, and full name are required"}), 400

    if confirm_password is not None and password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if role not in ["patient", "consultant"]:
        return jsonify({"error": "Role must be 'patient' or 'consultant'"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if role == "patient":
        profile = PatientProfile(
            user_id=user.id,
            full_name=full_name,
            phone_number=phone_number,
            age=data.get("age"),
            gender=data.get("gender"),
            disease_condition=data.get("disease_condition"),
            address=data.get("address"),
            emergency_contact=data.get("emergency_contact")
        )
        db.session.add(profile)
    else:
        profile = ConsultantProfile(
            user_id=user.id,
            full_name=full_name,
            phone_number=phone_number,
            designation=data.get("designation", "Consultant Physician"),
            specialization=data.get("specialization", "Internal Medicine"),
            organization=data.get("organization", "City Medical Hospital")
        )
        db.session.add(profile)

    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email}
    )

    return jsonify({
        "message": "Registration successful",
        "token": token,
        "access_token": token,
        "user": user.to_dict()
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "email": user.email}
    )

    return jsonify({
        "message": "Login successful",
        "token": token,
        "access_token": token,
        "user": user.to_dict()
    }), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"message": "Logout successful"}), 200
