from datetime import datetime, timezone
from app.extensions import db

class PatientProfile(db.Model):
    __tablename__ = "patient_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    disease_condition = db.Column(db.String(200), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    
    # Consultant assigned to this patient
    consultant_id = db.Column(db.Integer, db.ForeignKey("consultant_profiles.id", ondelete="SET NULL"), nullable=True, index=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    medicines = db.relationship("Medicine", backref="patient", lazy="dynamic", cascade="all, delete-orphan")
    dose_records = db.relationship("DoseRecord", backref="patient", lazy="dynamic", cascade="all, delete-orphan")
    feedbacks = db.relationship("Feedback", backref="patient", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.user.email if self.user else None,
            "phone_number": self.phone_number,
            "age": self.age,
            "gender": self.gender,
            "disease_condition": self.disease_condition,
            "address": self.address,
            "emergency_contact": self.emergency_contact,
            "consultant_id": self.consultant_id,
            "consultant_name": self.consultant.full_name if self.consultant else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
