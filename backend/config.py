import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///placement_portal.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    CHAT_WEBHOOK_URL = os.getenv("CHAT_WEBHOOK_URL", "")
    DAILY_REMINDER_HOUR = int(os.getenv("DAILY_REMINDER_HOUR", 8))
    DAILY_REMINDER_MINUTE = int(os.getenv("DAILY_REMINDER_MINUTE", 0))
    MONTHLY_REPORT_HOUR = int(os.getenv("MONTHLY_REPORT_HOUR", 9))
    MONTHLY_REPORT_MINUTE = int(os.getenv("MONTHLY_REPORT_MINUTE", 0))
    CELERY_TIMEZONE = os.getenv("CELERY_TIMEZONE", "UTC")
