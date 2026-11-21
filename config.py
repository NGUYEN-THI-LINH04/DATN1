import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    BASE_DIR / ".env",
    interpolate=False,
)


class Config:
    DB_SERVER = os.getenv("DB_SERVER", "")
    DB_NAME = os.getenv("DB_NAME", "")
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    SECRET_KEY = os.getenv("SECRET_KEY", "")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    APP_BASE_URL = os.getenv(
        "APP_BASE_URL",
        "http://127.0.0.1:5000",
    ).rstrip("/")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Máy đang chạy bằng HTTP tại localhost.
    # Khi triển khai bằng HTTPS sẽ chuyển thành True.
    SESSION_COOKIE_SECURE = False

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)