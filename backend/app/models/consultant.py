from datetime import datetime, timezone
from app.extensions import db

class ConsultantProfile(db.Model):
    __tablename__ = "consultant_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    designation = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    organization = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Assigned patients
    patients = db.relationship("PatientProfile", backref="consultant", lazy="dynamic")
    sent_feedbacks = db.relationship("Feedback", backref="consultant", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.user.email if self.user else None,
            "phone_number": self.phone_number,
            "designation": self.designation,
            "specialization": self.specialization,
            "organization": self.organization,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
