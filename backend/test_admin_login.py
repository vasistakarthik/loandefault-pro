import sqlite3
import bcrypt
from werkzeug.security import check_password_hash

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return check_password_hash(hashed, password)

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT email, password FROM users WHERE email = 'admin@sbi.com'")
user = cur.fetchone()
conn.close()

if user:
    print(f"Found user: {user['email']}")
    pw = "Admin@123"
    isValid = verify_password(pw, user['password'])
    print(f"Testing password '{pw}': {isValid}")
else:
    print("User not found.")
