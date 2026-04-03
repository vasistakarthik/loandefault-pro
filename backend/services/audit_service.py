import datetime
from backend.database.db import get_db_connection

def log_action(user_id, action, ip_address='', user_email=None, borrower_email=None, model_version=None, risk_level=None, input_data=None, shap_explanation=None):
    """Logs an action performed by a user with enhanced enterprise context."""
    conn = get_db_connection()
    try:
        conn.execute(
            """INSERT INTO audit_logs 
               (user_id, action, ip_address, user_email, borrower_email, model_version, risk_level, input_data, shap_explanation, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, action, ip_address, user_email, borrower_email, model_version, risk_level, input_data, shap_explanation, datetime.datetime.utcnow())
        )
        conn.commit()
    except Exception as e:
        print(f"Failed to log action: {e}")
    finally:
        conn.close()
