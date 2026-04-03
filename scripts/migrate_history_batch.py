import sqlite3
import os

db_path = os.path.join('backend', 'database', 'loan.db')

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE loan_history ADD COLUMN import_batch TEXT;")
        print("Successfully added import_batch column to loan_history.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column import_batch already exists.")
        else:
            print(f"Error: {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
