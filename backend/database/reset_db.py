import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'loan.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

tables = ['borrowers', 'customers', 'loan_applications', 'audit_logs']

for table in tables:
    try:
        cur.execute(f"DELETE FROM {table}")
        print(f"Cleared table: {table}")
    except Exception as e:
        print(f"Error clearing {table}: {e}")

# Also clear test users (keeping only the primary admin with ID 1)
try:
    cur.execute("DELETE FROM users WHERE id > 1")
    print("Cleared test users (Preserved Admin ID: 1)")
except Exception as e:
    print(f"Error clearing users: {e}")

# Reset sequences for a true clean start
try:
    all_tables = tables + ['users']
    for t in all_tables:
        cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = ?", (t,))
except: pass

conn.commit()
cur.execute("VACUUM")
conn.close()
print("Database maintenance completed on loan.db.")
print("System state set to 'Day Zero' (Only Admin profile exists).")
