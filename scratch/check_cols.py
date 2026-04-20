import sqlite3
import os

db_path = 'loan_default.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print(f"Tables: {tables}")
    for table_name in [t[0] for t in tables]:
        print(f"\nColumns for {table_name}:")
        cur.execute(f"PRAGMA table_info({table_name});")
        for col in cur.fetchall():
            print(col)
    conn.close()
else:
    print("Database not found at " + os.path.abspath(db_path))
