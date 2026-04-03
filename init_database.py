from backend.database.db import init_db
import os

print("Initializing database...")
try:
    init_db()
    print("Database verification complete. 'loan.db' is ready.")
except Exception as e:
    print(f"Error initializing database: {e}")

input("Press Enter to exit...")
