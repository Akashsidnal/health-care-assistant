import calendar
from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models.dose import DoseRecord
from app.models.medicine import Medicine
from app.models.schedule import MedicineSchedule

class AdherenceService:

    @staticmethod
    def auto_mark_missed_doses(patient_id: int, grace_period_minutes: int = 30):
        """
        Marks pending doses that passed scheduled time + grace period as MISSED.
        """
        now = datetime.now()
        pending_doses = DoseRecord.query.filter(
            DoseRecord.patient_id == patient_id,
            DoseRecord.status == "PENDING"
        ).all()

        updated_count = 0
        for dose in pending_doses:
            try:
                sched_dt = datetime.strptime(dose.scheduled_time, "%Y-%m-%d %H:%M")
                cutoff = sched_dt + timedelta(minutes=grace_period_minutes)
                if now > cutoff:
                    dose.status = "MISSED"
                    dose.actual_time = cutoff.strftime("%Y-%m-%d %H:%M:%S")
                    dose.notes = f"Automatically recorded missed after {grace_period_minutes} min timeout."
                    updated_count += 1
            except Exception:
                continue

        if updated_count > 0:
            db.session.commit()
        return updated_count

    @staticmethod
    def calculate_adherence(patient_id: int, start_dt_str: str = None, end_dt_str: str = None, medicine_id: int = None):
        """
        Calculates adherence percentage across Taken, Skipped, and Missed records.
        Adherence % = (Taken / (Taken + Skipped + Missed)) * 100
        Future pending doses are excluded from adherence denominator.
        """
        AdherenceService.auto_mark_missed_doses(patient_id)

        query = DoseRecord.query.filter(DoseRecord.patient_id == patient_id)

        if medicine_id:
            query = query.filter(DoseRecord.medicine_id == medicine_id)

        if start_dt_str:
            query = query.filter(DoseRecord.scheduled_time >= start_dt_str)
        if end_dt_str:
            query = query.filter(DoseRecord.scheduled_time <= end_dt_str)

        all_doses = query.all()

        taken_count = sum(1 for d in all_doses if d.status == "TAKEN")
        skipped_count = sum(1 for d in all_doses if d.status == "SKIPPED")
        missed_count = sum(1 for d in all_doses if d.status == "MISSED")
        pending_count = sum(1 for d in all_doses if d.status == "PENDING")

        total_evaluated = taken_count + skipped_count + missed_count
        percentage = round((taken_count / total_evaluated * 100), 1) if total_evaluated > 0 else 100.0

        return {
            "taken": taken_count,
            "skipped": skipped_count,
            "missed": missed_count,
            "pending": pending_count,
            "total_evaluated": total_evaluated,
            "percentage": percentage
        }

    @staticmethod
    def get_patient_adherence_summary(patient_id: int):
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        week_ago_str = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
        month_ago_str = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M")

        today_stats = AdherenceService.calculate_adherence(patient_id, start_dt_str=f"{today_str} 00:00", end_dt_str=f"{today_str} 23:59")
        week_stats = AdherenceService.calculate_adherence(patient_id, start_dt_str=week_ago_str)
        month_stats = AdherenceService.calculate_adherence(patient_id, start_dt_str=month_ago_str)
        overall_stats = AdherenceService.calculate_adherence(patient_id)

        # Per-medicine breakdown
        medicines = Medicine.query.filter_by(patient_id=patient_id).all()
        med_breakdown = []
        for med in medicines:
            med_stat = AdherenceService.calculate_adherence(patient_id, medicine_id=med.id)
            med_breakdown.append({
                "medicine_id": med.id,
                "medicine_name": med.name,
                "dosage": med.dosage,
                "is_active": med.is_active,
                **med_stat
            })

        # 7-day trend history for charts
        trend_days = []
        for i in range(6, -1, -1):
            day_dt = now - timedelta(days=i)
            day_str = day_dt.strftime("%Y-%m-%d")
            label = day_dt.strftime("%b %d")
            day_stats = AdherenceService.calculate_adherence(patient_id, start_dt_str=f"{day_str} 00:00", end_dt_str=f"{day_str} 23:59")
            trend_days.append({
                "date": day_str,
                "label": label,
                "taken": day_stats["taken"],
                "skipped": day_stats["skipped"],
                "missed": day_stats["missed"],
                "percentage": day_stats["percentage"]
            })

        return {
            "today": today_stats,
            "this_week": week_stats,
            "this_month": month_stats,
            "overall": overall_stats,
            "trend_7_days": trend_days,
            "medicines": med_breakdown
        }

    @staticmethod
    def get_month_calendar_data(patient_id: int, year: int, month: int):
        """
        Generates day-by-day status matrix for monthly calendar view.
        Returns days array with date, day number, dose counts and status flags.
        """
        AdherenceService.auto_mark_missed_doses(patient_id)
        num_days = calendar.monthrange(year, month)[1]
        
        days_data = []
        for day in range(1, num_days + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            doses = DoseRecord.query.filter(
                DoseRecord.patient_id == patient_id,
                DoseRecord.scheduled_time.startswith(date_str)
            ).all()

            taken = sum(1 for d in doses if d.status == "TAKEN")
            skipped = sum(1 for d in doses if d.status == "SKIPPED")
            missed = sum(1 for d in doses if d.status == "MISSED")
            pending = sum(1 for d in doses if d.status == "PENDING")

            status = "empty"
            if doses:
                if missed > 0:
                    status = "missed"
                elif skipped > 0:
                    status = "skipped"
                elif taken > 0:
                    status = "taken"
                else:
                    status = "pending"

            days_data.append({
                "day": day,
                "date": date_str,
                "total_doses": len(doses),
                "taken": taken,
                "skipped": skipped,
                "missed": missed,
                "pending": pending,
                "status": status,
                "doses": [d.to_dict() for d in doses]
            })

        return {
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "days": days_data
        }
