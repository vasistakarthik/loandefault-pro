import sqlite3
import os

BASE_DIR = r"c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database"
db_path = os.path.join(BASE_DIR, "loan.db")

if not os.path.exists(db_path):
    print("Database not found")
    exit(1)

conn = sqlite3.connect(db_path)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for (table,) in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count}")
conn.close()
