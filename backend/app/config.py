import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND / '.env')


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///learnhub.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('COOKIE_SECURE', 'false').lower() == 'true'
    MAX_CONTENT_LENGTH = 128 * 1024
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '').strip()
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-flash')
    DEEPSEEK_TIMEOUT = float(os.getenv('DEEPSEEK_TIMEOUT', '45'))
    RATE_LIMIT_ENABLED = True
