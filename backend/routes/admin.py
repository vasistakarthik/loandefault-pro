from flask import Blueprint, render_template, current_app
from flask_login import login_required
from ..utils.decorators import role_required
from ..services.audit_service import log_action
import json
import os
from flask import request, session

from ..database.db import get_db_connection
from ..database.models import User
import sqlite3

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route("/users")
@login_required
@role_required('admin')
def user_management():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template("admin/user_management.html", users=users)

@admin_bp.route("/user/toggle-verify/<int:user_id>", methods=['POST'])
@login_required
@role_required('admin')
def toggle_verify(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT is_verified FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        new_status = 0 if user['is_verified'] else 1
        conn.execute('UPDATE users SET is_verified = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
    conn.close()
    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}

@admin_bp.route("/user/toggle-active/<int:user_id>", methods=['POST'])
@login_required
@role_required('admin')
def toggle_active(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT is_active FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        new_status = 0 if user['is_active'] else 1
        conn.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
    conn.close()
    return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}

@admin_bp.route("/audit-logs")
@login_required
@role_required('admin')
def audit_logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 500').fetchall()
    conn.close()
    return render_template("admin/audit_logs.html", logs=logs)

@admin_bp.route("/model-metrics")
@login_required
@role_required('admin')
def model_metrics():
    try:
        from ..services.model_registry import ModelRegistry
        models = ModelRegistry.list_models()
        active_model = ModelRegistry.get_active_model()
        
        # User logging
        user_id = session.get('user_id')
        if user_id:
            log_action(user_id, 'Admin Access: Model Monitoring', request.remote_addr)

        return render_template("admin/model_monitoring.html", 
                             models=models, 
                             active_model=active_model)
    except Exception as e:
        current_app.logger.error(f"Admin Metrics Error: {e}")
        return "Internal Server Error", 500

@admin_bp.route("/train-model", methods=['POST'])
@login_required
@role_required('admin')
def trigger_training():
    """Enterprise MLOps: Automated Retraining Trigger"""
    try:
        from ..model.train_model import train
        result = train()
        
        user_id = session.get('user_id')
        if user_id:
            log_action(user_id, f"Triggered Model Retraining: {result.get('success')}", request.remote_addr)
            
        return json.dumps(result), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'success': False, 'message': str(e)}), 500, {'Content-Type': 'application/json'}

@admin_bp.route("/activate-model/<version>", methods=['POST'])
@login_required
@role_required('admin')
def activate_model(version):
    """Enterprise MLOps: Manually Switch Active Model"""
    from ..services.model_registry import ModelRegistry
    try:
        ModelRegistry.set_active_model(version)
        # Clear cache in predict.py after switch
        from ..model import predict
        predict._cached_model = None
        predict._cached_explainer = None
        
        return json.dumps({'success': True}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'success': False, 'message': str(e)}), 500, {'Content-Type': 'application/json'}

