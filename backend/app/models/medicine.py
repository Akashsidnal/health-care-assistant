from datetime import datetime, timezone
from app.extensions import db

class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    photo_filename = db.Column(db.String(255), nullable=True)
    prescription_doc = db.Column(db.String(255), nullable=True) # Uploaded prescription slip
    dosage = db.Column(db.String(100), nullable=False)
    tablet_count = db.Column(db.Integer, default=30)
    frequency = db.Column(db.String(100), default="Every day")
    instructions = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    schedules = db.relationship("MedicineSchedule", backref="medicine", lazy="dynamic", cascade="all, delete-orphan")
    dose_records = db.relationship("DoseRecord", backref="medicine", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_schedules=True):
        data = {
            "id": self.id,
            "patient_id": self.patient_id,
            "name": self.name,
            "photo_filename": self.photo_filename,
            "photo_url": f"/static/uploads/{self.photo_filename}" if self.photo_filename else None,
            "prescription_doc": self.prescription_doc,
            "prescription_url": f"/static/uploads/{self.prescription_doc}" if self.prescription_doc else None,
            "dosage": self.dosage,
            "tablet_count": self.tablet_count,
            "frequency": self.frequency,
            "instructions": self.instructions,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        if include_schedules:
            data["schedules"] = [s.to_dict() for s in self.schedules.all()]
        return data
