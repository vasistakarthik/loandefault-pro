import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "dev_key"
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or "jwt-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 86400 * 30  # 30 days
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_COOKIE_CSRF_PROTECT = False  # For now set to False to simplify AJAX login, but we use flask-wtf CSRF anyway
    JWT_COOKIE_SECURE = os.environ.get("ENV") == "production"
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRFToken"
    
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get("ENV") == "production"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database (Using SQLite for dev, configurable for production)
    DATABASE_URI = os.environ.get('DATABASE_URL') or os.path.join(BASE_DIR, 'database', 'loan.db')

    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Logging Configuration
    LOG_FILE = os.path.join(BASE_DIR, '..', 'logs', 'app.log')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
