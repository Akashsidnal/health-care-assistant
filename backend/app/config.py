import os
import socket
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "medicare-cloud-auth-secure-token-2026-cityeng")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "medicare-cloud-jwt-secret-key-32-chars-long")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        DATABASE_URL = f"sqlite:///{BASE_DIR / 'medicare_cloud.db'}"
    elif DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "web" / "static" / "uploads"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}
    
    # Adherence Grace Period (in minutes)
    GRACE_PERIOD_MINUTES = int(os.environ.get("GRACE_PERIOD_MINUTES", 30))
    
    # Network IP
    HOST_IP = get_local_ip()

class DevelopmentConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "medicare-testing-jwt-secret-key-32-chars-long"

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
