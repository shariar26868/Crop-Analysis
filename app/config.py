import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST", os.getenv("HOST", "localhost"))
DB_PORT = os.getenv("DB_PORT", os.getenv("PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", os.getenv("DB", "agriculture_db"))
DB_USER = os.getenv("DB_USER", os.getenv("USER", "user"))
DB_PASS = os.getenv("DB_PASS", os.getenv("PASSWORD", "password"))

ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000"
).split(",") if origin.strip()]

RATE_LIMIT = os.getenv("RATE_LIMIT", "60 per minute")
APP_ENV = os.getenv("APP_ENV", "development")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
CACHE_DEFAULT_EXPIRE = int(os.getenv("CACHE_DEFAULT_EXPIRE", "120"))
#default
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "adminpass")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
