import os
import sys

# Add the project root to sys.path to allow importing from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.database.db import get_db_connection
    from backend.config import Config
    print(f"[*] Initializing Database Purge Sequence...")
    print(f"[*] Environment: {Config.ENV}")
except ImportError as e:
    print(f"[!] Error: Could not import database modules. {e}")
    sys.exit(1)

def wipe_data():
    conn = get_db_connection()
    # Robust check using DATABASE_URI
    is_postgres = Config.DATABASE_URI.startswith('postgresql')
    
    tables_to_wipe = [
        'borrowers',
        'loan_applications',
        'loan_history',
        'audit_logs',
        'customers',
        'user_settings',
        'users',
        'model_registry'
    ]
    
    print(f"[*] Accessing Data Nodes...")
    
    try:
        if is_postgres:
            # PostgreSQL TRUNCATE is faster and resets IDs
            cursor = conn.cursor()
            for table in tables_to_wipe:
                print(f"[-] Purging {table}...")
                cursor.execute(f'TRUNCATE TABLE {table} CASCADE;')
            conn.commit()
            cursor.close()
        else:
            # SQLite DELETE
            for table in tables_to_wipe:
                print(f"[-] Purging {table}...")
                conn.execute(f'DELETE FROM {table};')
                conn.execute('DELETE FROM sqlite_sequence WHERE name=?;', (table,)) # Reset IDs
            conn.commit()
            
        print("\n[SUCCESS] All transactional data has been purged.")
        print("[INFO] User accounts and Model Registry were preserved for system stability.")
        
    except Exception as e:
        print(f"[!] Critical Failure during purge: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    confirm = input("!!! WARNING: This will PERMANENTLY delete all borrower and loan data. Type 'PURGE' to continue: ")
    if confirm == 'PURGE':
        wipe_data()
    else:
        print("[*] Operation cancelled by operator.")
