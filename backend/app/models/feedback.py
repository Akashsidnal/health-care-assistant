from datetime import datetime, timezone
from app.extensions import db

class Feedback(db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    consultant_id = db.Column(db.Integer, db.ForeignKey("consultant_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "consultant_id": self.consultant_id,
            "consultant_name": self.consultant.full_name if self.consultant else None,
            "patient_id": self.patient_id,
            "patient_name": self.patient.full_name if self.patient else None,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
