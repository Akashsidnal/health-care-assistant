import io
import csv
from datetime import datetime
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from app.models.patient import PatientProfile
from app.models.dose import DoseRecord
from app.services.adherence_service import AdherenceService

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@reports_bp.route("/csv", methods=["GET"])
@jwt_required()
def export_csv():
    patient_id = request.args.get("patient_id")
    if not patient_id:
        return jsonify({"error": "patient_id is required"}), 400

    patient = PatientProfile.query.get(int(patient_id))
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    query = DoseRecord.query.filter_by(patient_id=patient.id)
    if start_date:
        query = query.filter(DoseRecord.scheduled_time >= start_date)
    if end_date:
        query = query.filter(DoseRecord.scheduled_time <= end_date)

    doses = query.order_by(DoseRecord.scheduled_time.asc()).all()
    stats = AdherenceService.calculate_adherence(patient.id, start_date, end_date)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["MEDICARE CLOUD ADHERENCE REPORT"])
    writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow(["Patient Name", patient.full_name])
    writer.writerow(["Patient Phone", patient.phone_number])
    writer.writerow(["Condition", patient.disease_condition or "N/A"])
    writer.writerow(["Consultant", patient.consultant.full_name if patient.consultant else "Unassigned"])
    writer.writerow(["Overall Adherence", f"{stats['percentage']}%"])
    writer.writerow(["Total Taken Doses", stats["taken"]])
    writer.writerow(["Total Skipped Doses", stats["skipped"]])
    writer.writerow(["Total Missed Doses", stats["missed"]])
    writer.writerow([])
    writer.writerow(["Dose ID", "Medicine Name", "Dosage", "Scheduled Time", "Actual Action Time", "Status", "Notes"])

    for d in doses:
        writer.writerow([
            d.id,
            d.medicine.name if d.medicine else "N/A",
            d.medicine.dosage if d.medicine else "N/A",
            d.scheduled_time,
            d.actual_time or "N/A",
            d.status,
            d.notes or ""
        ])

    csv_data = output.getvalue()
    filename = f"MediCare_Report_{patient.full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@reports_bp.route("/summary/<int:patient_id>", methods=["GET"])
@jwt_required()
def get_report_data(patient_id):
    patient = PatientProfile.query.get(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    stats = AdherenceService.calculate_adherence(patient.id, start_date, end_date)
    medicines = [m.to_dict() for m in patient.medicines.all()]

    return jsonify({
        "generated_at": datetime.now().isoformat(),
        "patient": patient.to_dict(),
        "consultant": patient.consultant.to_dict() if patient.consultant else None,
        "date_range": {
            "start": start_date or "All time",
            "end": end_date or "Present"
        },
        "adherence": stats,
        "medicines": medicines
    }), 200
