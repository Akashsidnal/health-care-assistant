import os
from flask import Blueprint, render_template, redirect, url_for, send_from_directory, current_app

web_bp = Blueprint("web", __name__, template_folder="../../web/templates", static_folder="../../web/static")

@web_bp.route("/")
def index():
    return redirect(url_for("web.login"))

@web_bp.route("/login")
def login():
    return render_template("login.html")

@web_bp.route("/register")
def register():
    return render_template("register.html")

# Consultant Views
@web_bp.route("/dashboard")
@web_bp.route("/consultant/dashboard")
def consultant_dashboard():
    return render_template("consultant/dashboard.html")

@web_bp.route("/patients")
@web_bp.route("/consultant/patients")
def consultant_patients():
    return render_template("consultant/patients.html")

@web_bp.route("/patients/<int:patient_id>")
@web_bp.route("/consultant/patients/<int:patient_id>")
def consultant_patient_detail(patient_id):
    return render_template("consultant/patient_detail.html", patient_id=patient_id)

@web_bp.route("/reports")
@web_bp.route("/consultant/reports")
def consultant_reports():
    return render_template("consultant/reports.html")

@web_bp.route("/feedback")
@web_bp.route("/consultant/feedback")
def consultant_feedback():
    return render_template("consultant/feedback.html")

# Patient Views
@web_bp.route("/patient/dashboard")
def patient_dashboard():
    return render_template("patient/dashboard.html")

@web_bp.route("/patient/prescriptions")
def patient_prescriptions():
    return render_template("patient/prescriptions.html")

@web_bp.route("/patient/calendar")
def patient_calendar():
    return render_template("patient/calendar.html")

@web_bp.route("/patient/history")
def patient_history():
    return render_template("patient/history.html")

# PWA & Static Upload Routes
@web_bp.route("/manifest.json")
def manifest():
    return send_from_directory(current_app.static_folder, "manifest.json", mimetype="application/manifest+json")

@web_bp.route("/sw.js")
def service_worker():
    return send_from_directory(current_app.static_folder, "sw.js", mimetype="application/javascript")

@web_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_folder, filename)
