import sqlite3
import os

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, name, email, is_active, is_verified, role FROM users")
users = cur.fetchall()
for user in users:
    print(dict(user))
conn.close()
