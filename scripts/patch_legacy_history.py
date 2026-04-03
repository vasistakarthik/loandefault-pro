import sqlite3
import os

db_path = os.path.join('backend', 'database', 'loan.db')

def update_legacy():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE loan_history SET import_batch = 'LEGACY_DATA' WHERE import_batch IS NULL;")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Updated {count} legacy records to 'LEGACY_DATA'.")

if __name__ == "__main__":
    update_legacy()
