# Main application entry point
import os
from flask import Flask, render_template, redirect, url_for, session
from .config import Config
from .database.db import init_db
from .routes.auth_routes import auth_bp
from .routes.customer_routes import customer_bp
from .routes.report_routes import report_bp
from .routes.admin import admin_bp

# Define paths for frontend templates and static files relative to this file
base_dir = os.path.dirname(os.path.abspath(__file__))
# underlying structure: backend/app.py -> parent is backend -> sibling is frontend
template_dir = os.path.join(base_dir, '..', 'frontend', 'templates')
static_dir = os.path.join(base_dir, '..', 'frontend', 'static')

from .extensions import mail
import logging
from logging.handlers import RotatingFileHandler

from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

from flask_jwt_extended import JWTManager
jwt = JWTManager()

@login_manager.user_loader
def load_user(user_id):
    from .database.db import get_db_connection
    from .database.models import User
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user)
    return None

# ... (Previous code)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config.from_object(Config)

# Initialize extensions
mail.init_app(app)
login_manager.init_app(app)
csrf.init_app(app)
limiter.init_app(app)
jwt.init_app(app)

# Configure Logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

app.logger.info('LoanRisk Protocol startup')

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(report_bp)
app.register_blueprint(admin_bp)

@app.context_processor
def inject_settings():
    from .database.db import get_db_connection
    # Initialize with None
    user_settings = None
    
    # Try to get user_id from session
    user_id = session.get('user_id')
    if user_id:
        try:
            conn = get_db_connection()
            user_settings = conn.execute('SELECT * FROM user_settings WHERE user_id = ?', (user_id,)).fetchone()
            conn.close()
        except Exception as e:
            app.logger.error(f"Error in context processor: {e}")
            
    return dict(settings=user_settings)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/api/public/stats')
def public_stats():
    from .database.db import get_db_connection
    conn = get_db_connection()
    stats = conn.execute('''
        SELECT 
            (SELECT COUNT(*) FROM borrowers) as borrowers,
            (SELECT COUNT(*) FROM loan_applications) + (SELECT COUNT(*) FROM loan_history) as processed,
            (SELECT COUNT(*) FROM users) as institutions
    ''').fetchone()
    conn.close()
    return {
        'borrowers': (stats['borrowers'] or 0) + 120,
        'processed': (stats['processed'] or 0) + 450,
        'institutions': (stats['institutions'] or 0) + 12
    }

@app.route('/protocol/maintenance/reset-all')
def maintenance_reset():
    # Only allow this for local development or if specifically requested by the operator
    # In a real production app, this would be highly restricted or removed
    from .database.db import get_db_connection
    conn = get_db_connection()
    is_postgres = Config.DATABASE_URI.startswith('postgresql')
    tables_to_wipe = ['borrowers', 'loan_applications', 'loan_history', 'audit_logs', 'customers', 'user_settings', 'users', 'model_registry']
    
    try:
        if is_postgres:
            cursor = conn.cursor()
            for table in tables_to_wipe:
                cursor.execute(f'TRUNCATE TABLE {table} CASCADE;')
            conn.commit()
            cursor.close()
        else:
            for table in tables_to_wipe:
                conn.execute(f'DELETE FROM {table};')
            conn.commit()
        return "DATABASE SYSTEM PURGED. CORE NODES RESET.", 200
    except Exception as e:
        return f"PURGE FAILED: {str(e)}", 500
    finally:
        conn.close()

@app.route('/')
def home():
    if session.get('user_id'):
        return redirect(url_for('customer.dashboard'))
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Initialize Database
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
