import sys
import os
from werkzeug.security import generate_password_hash

# Add parent directory to path to import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.database.db import get_db_connection

def seed_admin():
    conn = get_db_connection()
    # Check if admin exists
    admin = conn.execute("SELECT id FROM users WHERE email = 'admin@sbi.com'").fetchone()
    
    if not admin:
        # Using a default password 'Admin@123' hashed for security
        hashed_pw = generate_password_hash('Admin@123')
        conn.execute('''
            INSERT INTO users (name, email, password, role, is_active, is_verified, bank, employee_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Sovereign Admin', 'admin@sbi.com', hashed_pw, 'Admin', 1, 1, 'SBI', 'SBI-ADMIN-001'))
        conn.commit()
        print("Sovereign Admin account created: admin@sbi.com / Admin@123")
    else:
        print("Admin account already exists.")
    conn.close()

if __name__ == "__main__":
    seed_admin()
