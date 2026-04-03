import sqlite3
import os

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE customers ADD COLUMN interest_rate REAL")
        print("Added interest_rate to customers")
    except sqlite3.OperationalError:
        print("interest_rate already exists or table doesn't exist")
        
    try:
        cur.execute("ALTER TABLE customers ADD COLUMN bank TEXT")
        print("Added bank to customers")
    except sqlite3.OperationalError:
        print("bank already exists or table doesn't exist")
        
    conn.commit()
    conn.close()
    print("Migration complete")
else:
    print(f"Database not found at {db_path}")
