from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify, make_response
from datetime import datetime, timedelta
from ..security.password_utils import verify_password, hash_password
from flask_login import login_user, logout_user, login_required, current_user
from ..database.models import User
from ..database.db import get_db_connection
from ..services.audit_service import log_action
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies

auth_bp = Blueprint('auth', __name__)

from ..utils.email_utils import send_mail

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,)).fetchone()
        conn.close()
        
        if user:
            is_valid = False
            try:
                is_valid = verify_password(password, user['password'])
            except ValueError:
                from werkzeug.security import check_password_hash
                if check_password_hash(user['password'], password):
                    is_valid = True
                    new_hash = hash_password(password)
                    conn = get_db_connection()
                    conn.execute('UPDATE users SET password = ? WHERE id = ?', (new_hash, user['id']))
                    conn.commit()
                    conn.close()

            if is_valid:
                # Stage 1: Email Verification Check
                if not user['is_verified']:
                    flash('Strategic clearance pending: Email verification required.', 'warning')
                    return redirect(url_for('auth.login'))

                # Stage 2: Admin Approval Check (is_active)
                if not user['is_active']:
                    flash('Account on hold: Administrative node activation required. Please contact your supervisor.', 'caution')
                    return redirect(url_for('auth.login'))

                conn = get_db_connection()
                conn.execute('UPDATE users SET last_login = ? WHERE id = ?', (datetime.utcnow(), user['id']))
                conn.commit()
                conn.close()

                # Login directly
                user_obj = User(user)
                login_user(user_obj)
                session.permanent = True
                
                # Convert to dict for safe .get()
                u_data = dict(user)
                session['user_id'] = u_data['id']
                session['username'] = u_data['name']
                session['role'] = u_data['role']
                session['email'] = u_data['email']
                session['bank'] = u_data.get('bank', 'SBI')

                log_action(user['id'], 'Login', request.remote_addr, user_email=user['email'])

                flash('Access granted. Initializing session...', 'success')
                return redirect(url_for('customer.dashboard'))
            else:
                flash('Access Denied: Invalid credentials.', 'error')
        else:
            flash('Access Denied: Node not found.', 'error')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    user_id = session.get('user_id')
    if user_id:
        log_action(user_id, 'Logout', request.remote_addr)
    logout_user()
    session.clear()
    flash('Successfully exited secure vault.', 'info')
    return redirect(url_for('home'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # ... (existing register logic) ...
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        role = request.form.get('role', 'analyst')
        
        conn = get_db_connection()
        
        # Check if email already exists
        user = conn.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,)).fetchone()
        
        if user:
            flash('Email address already exists', 'error')
            conn.close()
            return redirect(url_for('auth.register'))
            
        hashed_password = hash_password(password)
        bank = request.form.get('bank', 'SBI')
        employee_id = request.form.get('employee_id', '')
        
        import uuid
        verification_token = str(uuid.uuid4())
        
        try:
            # AUTO-VERIFY and AUTO-ACTIVE for UX (Per User Request)
            conn.execute('INSERT INTO users (name, email, password, role, is_verified, is_active, verification_token, bank, employee_id) VALUES (?, ?, ?, ?, 1, 1, ?, ?, ?)', 
                         (name, email, hashed_password, role, verification_token, bank, employee_id))
            conn.commit()
            
            # Prepare Verification/Welcome Email
            link = current_app.config.get('APP_URL', '') + url_for('auth.verify_email', token=verification_token)
            subject = "Account Activated - LoanDefault Pro"
            html_body = f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
                <h2 style="color: #0f172a;">Welcome to LoanDefault Pro</h2>
                <p>Hello {name},</p>
                <p>Your institutional access has been established. You can log in immediately to our risk intelligence platform.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Access Dashboard</a>
                </div>
                <p>Status: <strong style="color: #10b981;">Active</strong></p>
                <p>If the button doesn't work, copy and paste this link:</p>
                <p style="word-break: break-all; color: #64748b;">{link}</p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                <p style="font-size: 0.875rem; color: #94a3b8;">Welcome aboard. For security inquiries, please contact your local node administrator.</p>
            </div>
            """
            
            email_sent = send_mail(email, subject, html_content=html_body)
            
            if email_sent:
                flash('Strategic clearance granted. Verification email transmitted successfully.', 'success')
            else:
                flash('Registration successful! Account activated. (Node link bypass enabled - Email delivery delayed)', 'info')
                current_app.logger.warning(f"Email delivery failed for {email}")
            
            # Initialize default settings for new user
            user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            conn.execute('INSERT INTO user_settings (user_id) VALUES (?)', (user_id,))
            conn.commit()

            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
        finally:
            conn.close()
            
    return render_template('register.html')

@auth_bp.route('/verify/<token>')
def verify_email(token):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE verification_token = ?', (token,)).fetchone()
    
    if user:
        conn.execute('UPDATE users SET is_verified = 1, verification_token = NULL WHERE id = ?', (user['id'],))
        conn.commit()
        flash('Email verified successfully! You can now login.', 'success')
    else:
        flash('Invalid or expired verification link.', 'error')
        
    conn.close()
    return redirect(url_for('auth.login'))


# --- FORGOT PASSWORD LOGIC ---
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def get_serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        print(f"[DEBUG] Password reset requested for: {email}")
        
        conn = get_db_connection()
        # Use LOWER() for case-insensitive matching in SQLite
        user = conn.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,)).fetchone()
        conn.close()
        
        if user:
            print(f"[DEBUG] User found in DB: {user['email']}")
            s = get_serializer()
            token = s.dumps(email, salt='password-reset-salt')
            link = current_app.config.get('APP_URL', '') + url_for('auth.reset_password', token=token)
            
            subject = "Password Reset Request - LoanDefault Pro"
            html_body = f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 10px;">
                <h2 style="color: #0f172a;">Password Reset Security Protocol</h2>
                <p>Hello,</p>
                <p>A request has been initiated to reset the security credentials for your LoanDefault Pro account. Click the button below to authorize this change:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background-color: #0ea5e9; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Authorize Reset</a>
                </div>
                <p>If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #64748b;">{link}</p>
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                <p style="font-size: 0.875rem; color: #94a3b8;">Status: <strong>Verification Required</strong>. This link expires in 30 minutes. If you did not request this, please contact support.</p>
            </div>
            """

            email_sent = send_mail(email, subject, html_body)

            if email_sent:
                print(f"[SUCCESS] Password reset email sent to {email}")
                flash('Password reset link has been sent to your email.', 'info')
            else:
                # FALLBACK FOR DEMO
                print(f"\n{'='*50}")
                print(f"[FALLBACK] Reset Link for {email}:")
                print(f"{link}")
                print(f"{'='*50}\n")
                flash('Email sending failed. Please check server logs or contact admin.', 'warning')

            return redirect(url_for('auth.login'))
        else:
            flash('Email not found.', 'error')
            
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = get_serializer()
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=1800) # 30 minutes expiration
    except Exception:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
            
        hashed_password = hash_password(password)
        
        conn = get_db_connection()
        conn.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_password, email))
        conn.commit()
        conn.close()
        
        flash('Your password has been updated! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('reset_password.html', token=token)

# --- REAL-TIME API ENDPOINTS ---

@auth_bp.route('/api/check-email', methods=['GET'])
def check_email():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
        
    conn = get_db_connection()
    user = conn.execute('SELECT id FROM users WHERE LOWER(email) = ?', (email.strip().lower(),)).fetchone()
    conn.close()
    
    if user:
        return jsonify({"available": False, "message": "Email already registered"}), 200
    return jsonify({"available": True, "message": "Email available"}), 200

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    name = data.get('name')
    email = data.get('email', '').strip().lower()
    password = data.get('password')
    role = data.get('role', 'Risk Analyst')
    employee_id = data.get('employee_id', '').strip().upper()
    
    import re
    if not re.match(r'^[A-Za-z\s]{3,}$', name):
        return jsonify({"error": "Name must be at least 3 characters and contain only letters/spaces"}), 400
        
    if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password):
        return jsonify({"error": "Password does not meet requirements"}), 400
        
    conn = get_db_connection()
    user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if user:
        conn.close()
        return jsonify({"error": "Email already exists"}), 409
        
    # --- INSTITUTIONAL VERIFICATION (Simulation) ---
    # In a real system, this checks against the Bank's central HR LDAP/SQL
    if not employee_id.startswith('BANK-'):
        conn.close()
        return jsonify({"error": "Invalid Employee ID. Must follow BANK-XXXX format."}), 403
        
    hashed_password = hash_password(password)
    
    try:
        bank = data.get('bank', 'SBI')
        # AUTO-VERIFY and AUTO-ACTIVE for API too
        cur = conn.execute('INSERT INTO users (name, email, password, role, is_verified, is_active, employee_id, bank) VALUES (?, ?, ?, ?, 1, 1, ?, ?)', 
                     (name, email, hashed_password, role, employee_id, bank))
        user_id = cur.lastrowid
        
        # Initialize default settings
        conn.execute('INSERT INTO user_settings (user_id) VALUES (?)', (user_id,))
        conn.commit()
        
        log_action(user_id, 'Registration (API - Auto-Approved)', 'Remote')
        
        return jsonify({
            "success": True, 
            "message": "Protocol Established: Account created and activated.",
            "redirect": url_for('auth.login')
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email.strip().lower(),)).fetchone()
    conn.close()
    
    if user:
        is_valid = False
        try:
            is_valid = verify_password(password, user['password'])
        except ValueError:
            from werkzeug.security import check_password_hash
            if check_password_hash(user['password'], password):
                is_valid = True
                # Upgrade to bcrypt hash
                new_hash = hash_password(password)
                conn = get_db_connection()
                conn.execute('UPDATE users SET password = ? WHERE id = ?', (new_hash, user['id']))
                conn.commit()
                conn.close()
        
        if is_valid:
            # --- ACCESS CONTROL CHECK ---
            if not user['is_verified']:
                return jsonify({"error": "Institutional Access Pending. Your account is awaiting Admin approval."}), 403

            user_obj = User(user)
            login_user(user_obj) # Keep session compatibility
            
            # Set custom session keys expected by the customer routes
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']
            
            identity = {"id": user['id'], "role": user['role']}
            access_token = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)
            
            resp = jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "message": "Login successful",
                "user": {
                    "id": user['id'],
                    "name": user['name'],
                    "role": user['role']
                }
            })
            
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            
            log_action(user['id'], 'Login (API)', request.remote_addr)
            
            return resp, 200
        
    return jsonify({"error": "Invalid credentials"}), 401



