import os
from dotenv import load_dotenv

# Find the project root (one level up from the 'backend' folder)
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '..', '.env')
load_dotenv(dotenv_path=env_path)

class Config:
    # 🔑 App Secrets
    SECRET_KEY = os.environ.get('SECRET_KEY') or "dev_key_change_me_in_production"
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or "jwt-secret-key-change-me"
    
    # 🕒 Expiration & Sessions
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # seconds
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 1800))  # 30 minutes
    
    # 🛡️ Security Settings
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_COOKIE_CSRF_PROTECT = os.environ.get('JWT_COOKIE_CSRF_PROTECT', 'False') == 'True'
    JWT_COOKIE_SECURE = os.environ.get("ENV") == "production"
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRFToken"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get("ENV") == "production"
    
    # 📁 Paths & Core
    ENV = os.environ.get("ENV", "development")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'loan.db')

    # 📧 Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # 📝 Logging & Diagnostics
    LOG_FILE = os.path.join(BASE_DIR, '..', 'logs', 'app.log')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 🚀 Server Config
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    APP_URL = os.environ.get('APP_URL', f"http://localhost:{PORT}").rstrip('/')
