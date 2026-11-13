import os
from flask import Flask, jsonify, request
from app.config import config_by_name
from app.extensions import db, jwt, cors

def create_app(config_name="development"):
    app = Flask(
        __name__,
        template_folder="../web/templates",
        static_folder="../web/static"
    )
    
    app_config = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(app_config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    from app.routes.auth import auth_bp
    from app.routes.patient import patient_bp
    from app.routes.consultant import consultant_bp
    from app.routes.medicines import medicines_bp
    from app.routes.doses import doses_bp
    from app.routes.adherence import adherence_bp
    from app.routes.feedback import feedback_bp
    from app.routes.sync import sync_bp
    from app.routes.reports import reports_bp
    from app.routes.web import web_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(consultant_bp)
    app.register_blueprint(medicines_bp)
    app.register_blueprint(doses_bp)
    app.register_blueprint(adherence_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(reports_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "project": "MediCare Cloud",
            "version": "1.0.0",
            "host_ip": app.config.get("HOST_IP", "127.0.0.1"),
            "database": app.config["SQLALCHEMY_DATABASE_URI"].split("://")[0]
        }), 200

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"error": "Missing or invalid authorization token"}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired, please log in again"}), 401

    return app
