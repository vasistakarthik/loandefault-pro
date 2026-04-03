import sqlite3
import os

try:
    db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Tables names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("Tables in database:", [t[0] for t in tables])
    
    for table_name in [t[0] for t in tables]:
        print(f"\n{table_name} Table Schema:")
        cur.execute(f"PRAGMA table_info({table_name})")
        rows = cur.fetchall()
        for row in rows:
            print(row)
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
