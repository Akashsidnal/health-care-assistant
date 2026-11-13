from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User

def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            
            if not user_role:
                identity = get_jwt_identity()
                user = User.query.get(int(identity))
                if not user:
                    return jsonify({"error": "User not found"}), 404
                user_role = user.role
                
            if user_role not in allowed_roles:
                return jsonify({
                    "error": "Forbidden: insufficient permissions",
                    "required_role": allowed_roles,
                    "your_role": user_role
                }), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def patient_required(fn):
    return role_required("patient")(fn)

def consultant_required(fn):
    return role_required("consultant")(fn)
