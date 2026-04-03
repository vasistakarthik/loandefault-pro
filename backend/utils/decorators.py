from functools import wraps
from flask import session, redirect, url_for, flash

def role_required(required_role):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "role" not in session:
                flash("Please log in to access this page.", "error")
                return redirect(url_for("auth.login"))

            role = session.get("role", "").lower()
            if required_role.lower() == "admin":
                # Broad match for administrative roles
                if "admin" not in role and "officer" not in role and "manager" not in role:
                    return "Unauthorized Access: Administrative privileges required", 403
            elif role != required_role.lower():
                return f"Unauthorized Access: {required_role} role required", 403

            return f(*args, **kwargs)
        return decorated_function
    return wrapper
