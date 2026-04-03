import sqlite3
import os

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\loan.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, is_active, is_verified, role FROM users")
        users = cur.fetchall()
        for user in users:
            print(dict(user))
    except Exception as e:
        print(f"Error reading users: {e}")
    conn.close()
else:
    print("Database not found at backend/loan.db")
