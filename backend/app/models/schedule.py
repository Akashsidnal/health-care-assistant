from datetime import datetime, timezone
from app.extensions import db

class MedicineSchedule(db.Model):
    __tablename__ = "medicine_schedules"

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_time = db.Column(db.String(10), nullable=False)   # "HH:MM" 24-hour format
    start_date = db.Column(db.String(10), nullable=False)       # "YYYY-MM-DD"
    end_date = db.Column(db.String(10), nullable=True)
    days_of_week = db.Column(db.String(100), default="EVERY_DAY")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    dose_records = db.relationship("DoseRecord", backref="schedule", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "medicine_id": self.medicine_id,
            "scheduled_time": self.scheduled_time,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "days_of_week": self.days_of_week,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
