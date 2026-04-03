
import os
import sqlite3

# Define the absolute path to the database
BASE_DIR = os.path.abspath(r"c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database")
DATABASE = os.path.join(BASE_DIR, "loan.db")

print("--- DIAGNOSTIC SCRIPT ---")
print(f"Checking for database at: {DATABASE}")

if not os.path.exists(DATABASE):
    print("ERROR: Database file NOT found at this path.")
else:
    print("SUCCESS: Database file found.")
    
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check Users Table
        print("\nChecking 'users' table...")
        try:
            users = cursor.execute("SELECT id, name, email FROM users").fetchall()
            if not users:
                print("⚠️ Table 'users' exists but is EMPTY.")
                print(f"Found {len(users)} users:")
                for user in users:
                    print(f"   - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
        except sqlite3.OperationalError as e:
            print(f"ERROR reading 'users' table: {e}")

        conn.close()
        
    except Exception as e:
        print(f"Major Check Failed: {e}")

print("\n--- END DIAGNOSTIC ---")
input("Press Enter to close...")
