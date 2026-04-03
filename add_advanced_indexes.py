import sqlite3
import os

BASE_DIR = r"c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database"
db_path = os.path.join(BASE_DIR, "loan.db")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("Applying advanced optimizations and indexes...")

# Functional Indexes for Case-Insensitive Search (if supported)
try:
    cur.execute("CREATE INDEX IF NOT EXISTS idx_borrowers_name_lower ON borrowers(LOWER(full_name))")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_borrowers_email_lower ON borrowers(LOWER(email))")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_name_lower ON customers(LOWER(name))")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_history_name_lower ON loan_history(LOWER(name))")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_history_email_lower ON loan_history(LOWER(email))")
    print("Functional indexes created.")
except sqlite3.OperationalError:
    print("Functional indexes not supported, falling back to COLLATE NOCASE indexes.")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_borrowers_name_nocase ON borrowers(full_name COLLATE NOCASE)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_borrowers_email_nocase ON borrowers(email COLLATE NOCASE)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_name_nocase ON customers(name COLLATE NOCASE)")

# Multi-column index for status lookups (used in last_status subqueries)
cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_apps_borrower_status_date ON loan_applications(borrower_id, created_at DESC, status)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_history_email_status_date ON loan_history(email, created_at DESC, status)")

conn.commit()
conn.close()

print("Optimizations applied.")
