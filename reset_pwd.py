import sqlite3
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db'
conn = sqlite3.connect(db_path)
new_hashed = hash_password("DemoPassword123!")
conn.execute("UPDATE users SET password = ? WHERE id = 5", (new_hashed,))
conn.commit()
conn.close()
print("Password updated for ID 5 (Admin)")
