from datetime import datetime, timezone
from app.extensions import db

class DoseRecord(db.Model):
    __tablename__ = "dose_records"
    __table_args__ = (
        db.UniqueConstraint("patient_id", "schedule_id", "scheduled_time", name="uq_patient_schedule_dose"),
    )

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey("medicine_schedules.id", ondelete="CASCADE"), nullable=True, index=True)
    
    scheduled_time = db.Column(db.String(25), nullable=False, index=True) # "YYYY-MM-DD HH:MM"
    actual_time = db.Column(db.String(25), nullable=True)                 # "YYYY-MM-DD HH:MM:SS"
    status = db.Column(db.String(20), nullable=False, default="PENDING", index=True) # "PENDING", "TAKEN", "SKIPPED", "MISSED"
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "medicine_id": self.medicine_id,
            "medicine_name": self.medicine.name if self.medicine else None,
            "photo_url": f"/static/uploads/{self.medicine.photo_filename}" if (self.medicine and self.medicine.photo_filename) else None,
            "dosage": self.medicine.dosage if self.medicine else None,
            "instructions": self.medicine.instructions if self.medicine else None,
            "schedule_id": self.schedule_id,
            "scheduled_time": self.scheduled_time,
            "actual_time": self.actual_time,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
