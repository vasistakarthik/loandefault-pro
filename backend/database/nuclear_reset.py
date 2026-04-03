import sys
import os

# Add parent directory to path to import backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.database.db import init_db

if __name__ == "__main__":
    print("Re-initializing Database...")
    init_db()
    print("Database Re-initialized successfully with clean tables and institutional schema.")
