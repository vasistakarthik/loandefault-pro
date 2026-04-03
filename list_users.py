import sqlite3
import os

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("Users found:")
    for u in users:
        print(f"ID: {u['id']}, Name: {u['name']}, Email: {u['email']}, Role: {u['role']}, Verified: {u['is_verified']}")
    conn.close()
else:
    print("Database not found.")
