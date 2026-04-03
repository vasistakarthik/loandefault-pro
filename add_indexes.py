import sqlite3
import os

# Enterprise Database Performance Optimization Script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'backend', 'database', 'loan.db')

print(f"Applying Enterprise Indexes to: {db_path}...")

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. OPTIMIZE LOAN_HISTORY: Core for risk evolution tracking
    print("- Indexing loan_history (borrower_id, created_at, status)...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_history_borrower_id ON loan_history(borrower_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_history_created_at ON loan_history(created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_history_status ON loan_history(status)")

    # 2. OPTIMIZE USERS: Optimize authentication and search
    print("- Indexing users (email)...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

    # 3. OPTIMIZE BORROWERS: Improve linkage between entities
    # Using 'id' since it's the primary linkage, although PKs are indexed, 
    # we'll ensure high-performance lookups.
    print("- Indexing borrowers (id)...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_borrowers_id ON borrowers(id)")

    # 4. ADDITIONAL PERFORMANCE BOOSTERS (From Previous Audit)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_loan_apps_borrower_id ON loan_applications(borrower_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)")

    conn.commit()
    conn.close()
    print("Optimization Complete.")

except Exception as e:
    print(f"Error optimizing database: {e}")
