import sqlite3
import os

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\loan_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check for existence of 'status' column in 'borrowers'
cursor.execute("PRAGMA table_info(borrowers)")
columns = [row[1] for row in cursor.fetchall()]

if 'status' not in columns:
    print("Column 'status' missing from 'borrowers'. Adding...")
    cursor.execute("ALTER TABLE borrowers ADD COLUMN status TEXT DEFAULT 'Pending'")
    conn.commit()
    print("Column 'status' added.")
else:
    print("Column 'status' already exists in 'borrowers'.")

conn.close()
