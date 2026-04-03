import sqlite3
import os

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan_default.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check if column exists
    cur.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]
    
    if 'bank' not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN bank TEXT DEFAULT 'SBI';")
        print("Added 'bank' column")
    if 'employee_id' not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN employee_id TEXT;")
        print("Added 'employee_id' column")
    
    conn.commit()
    conn.close()
else:
    print(f"DB not found at {db_path}")
