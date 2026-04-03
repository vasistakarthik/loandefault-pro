import sqlite3
import os

def get_db_connection():
    # Use current_app config if available (within Flask context)
    try:
        from flask import current_app
        db_path = current_app.config['DATABASE_URI']
    except (ImportError, RuntimeError):
        # Fallback for scripts outside Flask context
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(BASE_DIR, 'loan.db')
    
    # Check if it's a sqlite path or a connection string
    if db_path.startswith('sqlite://'):
        # For simplicity, if using sqlite URL, strip prefix for standard sqlite3
        db_path = db_path.replace('sqlite:///', '')
    
    # Generic connection logic (currently focusing on SQLite but prepared for URI)
    conn = sqlite3.connect(db_path, timeout=20) # 20 seconds timeout
    conn.row_factory = sqlite3.Row
    # Ensure busy timeout is set via PRAGMA as well
    conn.execute("PRAGMA busy_timeout = 20000")
    return conn


def init_db():
    conn = get_db_connection()
    
    # 1. Create tables if they don't exist (using schema.sql)
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    
    # 2. Check for missing columns in existing tables (Migration logic)
    cur = conn.cursor()
    
    # Check 'users' table for 'role' and 'created_at'
    try:
        cur.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cur.fetchall()]
        
        if 'role' not in columns:
            print("Migrating: Adding 'role' column to users table.")
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'analyst'")
            
        if 'created_at' not in columns:
            print("Migrating: Adding 'created_at' column to users table.")
            cur.execute("ALTER TABLE users ADD COLUMN created_at DATETIME")
            
        if 'is_active' not in columns:
            print("Migrating: Adding 'is_active' column to users table.")
            cur.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
            
        if 'last_login' not in columns:
            print("Migrating: Adding 'last_login' column to users table.")
            cur.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
            
        if 'verification_token' not in columns:
            print("Migrating: Adding 'verification_token' column to users table.")
            cur.execute("ALTER TABLE users ADD COLUMN verification_token TEXT")

        if 'is_verified' not in columns:
            print("Migrating: Adding 'is_verified' column to users table.")
            cur.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 1")
            
        if 'employee_id' not in columns:
            print("Migrating: Adding 'employee_id' column to users table.")
            cur.execute("ALTER TABLE users ADD COLUMN employee_id TEXT")
            
        if 'bank' not in columns:
            print("Migrating: Adding 'bank' column to users table.")
            cur.execute("ALTER TABLE users ADD COLUMN bank TEXT DEFAULT 'SBI'")

        # New: Audit Hashing for Zero-Trust
        cur.execute("PRAGMA table_info(loan_applications)")
        app_columns = [col[1] for col in cur.fetchall()]
        if 'record_hash' not in app_columns:
            print("Migrating: Adding 'record_hash' column to loan_applications.")
            cur.execute("ALTER TABLE loan_applications ADD COLUMN record_hash TEXT")

        cur.execute("PRAGMA table_info(customers)")
        cust_columns = [col[1] for col in cur.fetchall()]
        if 'record_hash' not in cust_columns:
            print("Migrating: Adding 'record_hash' column to customers.")
            cur.execute("ALTER TABLE customers ADD COLUMN record_hash TEXT")
            
    except Exception as e:
        print(f"Users migration check failed: {e}")

    # Check 'customers' table for 'loan_type' and 'risk_reason'
    try:
        cur.execute("PRAGMA table_info(customers)")
        columns = [info[1] for info in cur.fetchall()]
        
        if 'loan_type' not in columns:
            print("Migrating: Adding 'loan_type' column to customers table.")
            cur.execute("ALTER TABLE customers ADD COLUMN loan_type TEXT")
            
        if 'risk_reason' not in columns:
            print("Migrating: Adding 'risk_reason' column to customers table.")
            cur.execute("ALTER TABLE customers ADD COLUMN risk_reason TEXT")

        if 'prediction_result' not in columns: # Should exist, but checking just in case
             print("Migrating: Adding 'prediction_result' column to customers table.")
             cur.execute("ALTER TABLE customers ADD COLUMN prediction_result TEXT")

        if 'risk_probability' not in columns:
            print("Migrating: Adding 'risk_probability' column to customers table.")
            cur.execute("ALTER TABLE customers ADD COLUMN risk_probability REAL")
        
        if 'existing_emi' not in columns:
            print("Migrating: Adding 'existing_emi' column to customers table.")
            cur.execute("ALTER TABLE customers ADD COLUMN existing_emi REAL DEFAULT 0")

        if 'employment_type' not in columns:
            print("Migrating: Adding 'employment_type' column to customers table.")
            cur.execute("ALTER TABLE customers ADD COLUMN employment_type TEXT DEFAULT 'Salaried'")

        if 'tenure' not in columns:
            print("Migrating: Adding 'tenure' column to customers table.")
            cur.execute("ALTER TABLE customers ADD COLUMN tenure INTEGER DEFAULT 12")

        if 'status' not in columns:
            print("Migrating: Adding 'status' column to customers table.")
            cur.execute("ALTER TABLE customers ADD COLUMN status TEXT DEFAULT 'Pending'")

    except Exception as e:
        print(f"Migration check failed: {e}")

    # Check 'loan_history' table for extended columns
    try:
        cur.execute("PRAGMA table_info(loan_history)")
        columns = [info[1] for info in cur.fetchall()]
        
        if 'paid_amount' not in columns:
            print("Migrating: Adding 'paid_amount' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN paid_amount REAL DEFAULT 0")
        
        if 'balance_amount' not in columns:
            print("Migrating: Adding 'balance_amount' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN balance_amount REAL DEFAULT 0")

        if 'months_completed' not in columns:
            print("Migrating: Adding 'months_completed' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN months_completed INTEGER DEFAULT 0")

        if 'default_reason' not in columns:
            print("Migrating: Adding 'default_reason' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN default_reason TEXT")

        if 'import_batch' not in columns:
            print("Migrating: Adding 'import_batch' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN import_batch TEXT")

        if 'age' not in columns:
            print("Migrating: Adding 'age' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN age INTEGER")

        if 'credit_score' not in columns:
            print("Migrating: Adding 'credit_score' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN credit_score INTEGER")

        if 'annual_income' not in columns:
            print("Migrating: Adding 'annual_income' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN annual_income REAL")

        if 'employment_type' not in columns:
            print("Migrating: Adding 'employment_type' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN employment_type TEXT DEFAULT 'Salaried'")

        if 'loan_type' not in columns:
            print("Migrating: Adding 'loan_type' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN loan_type TEXT DEFAULT 'Personal Loan'")

        if 'existing_emi' not in columns:
            print("Migrating: Adding 'existing_emi' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN existing_emi REAL DEFAULT 0")

        if 'risk_score' not in columns:
            print("Migrating: Adding 'risk_score' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN risk_score REAL")

        if 'borrower_id' not in columns:
            print("Migrating: Adding 'borrower_id' to loan_history.")
            cur.execute("ALTER TABLE loan_history ADD COLUMN borrower_id INTEGER")

    except Exception as e:
        print(f"Loan history migration check failed: {e}")

    # Check 'model_registry' for MLOps columns
    try:
        cur.execute("PRAGMA table_info(model_registry)")
        columns = [info[1] for info in cur.fetchall()]
        
        if 'path' not in columns:
            print("Migrating: Adding 'path' and 'is_active' to model_registry.")
            cur.execute("ALTER TABLE model_registry ADD COLUMN path TEXT")
            cur.execute("ALTER TABLE model_registry ADD COLUMN is_active INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE model_registry ADD COLUMN f1_score REAL")
            cur.execute("ALTER TABLE model_registry ADD COLUMN metadata TEXT")
    except Exception as e:
        print(f"Model registry migration check failed: {e}")

    # Check 'audit_logs' for Governance columns
    try:
        cur.execute("PRAGMA table_info(audit_logs)")
        columns = [info[1] for info in cur.fetchall()]
        
        governance_cols = [
            ('user_id', 'INTEGER'),
            ('user_email', 'TEXT'),
            ('ip_address', 'TEXT'),
            ('borrower_email', 'TEXT'),
            ('model_version', 'TEXT'),
            ('risk_level', 'TEXT'),
            ('input_data', 'TEXT'),
            ('shap_explanation', 'TEXT')
        ]
        
        for col, typ in governance_cols:
            if col not in columns:
                print(f"Migrating: Adding '{col}' to audit_logs.")
                cur.execute(f"ALTER TABLE audit_logs ADD COLUMN {col} {typ}")

    except Exception as e:
        print(f"Audit logs governance migration failed: {e}")

    # Check 'borrowers' table for 'status', 'creation_source', and clustering fields
    try:
        cur.execute("PRAGMA table_info(borrowers)")
        columns = [info[1] for info in cur.fetchall()]
        
        if 'status' not in columns:
            print("Migrating: Adding 'status' column to borrowers table.")
            cur.execute("ALTER TABLE borrowers ADD COLUMN status TEXT DEFAULT 'Pending'")
            
        if 'creation_source' not in columns:
            print("Migrating: Adding 'creation_source' column to borrowers table.")
            cur.execute("ALTER TABLE borrowers ADD COLUMN creation_source TEXT DEFAULT 'Manual'")

        if 'physical_address' not in columns:
            print("Migrating: Adding 'physical_address' to borrowers.")
            cur.execute("ALTER TABLE borrowers ADD COLUMN physical_address TEXT")

        if 'contact_phone' not in columns:
            print("Migrating: Adding 'contact_phone' to borrowers.")
            cur.execute("ALTER TABLE borrowers ADD COLUMN contact_phone TEXT")
            
        if 'paid_amount' not in columns:
            print("Migrating: Adding 'paid_amount' to borrowers.")
            cur.execute("ALTER TABLE borrowers ADD COLUMN paid_amount REAL DEFAULT 0")

        if 'balance_amount' not in columns:
            print("Migrating: Adding 'balance_amount' to borrowers.")
            cur.execute("ALTER TABLE borrowers ADD COLUMN balance_amount REAL DEFAULT 0")

    except Exception as e:
        print(f"Borrowers migration check failed: {e}")

    # Sync clustering fields to loan_history
    try:
        cur.execute("PRAGMA table_info(loan_history)")
        h_columns = [info[1] for info in cur.fetchall()]
        if 'physical_address' not in h_columns:
            cur.execute("ALTER TABLE loan_history ADD COLUMN physical_address TEXT")
        if 'contact_phone' not in h_columns:
            cur.execute("ALTER TABLE loan_history ADD COLUMN contact_phone TEXT")
    except: pass

    # Check 'user_settings' for thresholds and theme
    try:
        cur.execute("PRAGMA table_info(user_settings)")
        columns = [info[1] for info in cur.fetchall()]
        
        settings_cols = [
            ('low_threshold', 'INTEGER DEFAULT 40'),
            ('med_threshold', 'INTEGER DEFAULT 70'),
            ('algorithm', 'TEXT DEFAULT "XGBoost"'),
            ('ai_enabled', 'INTEGER DEFAULT 1'),
            ('auto_retrain', 'INTEGER DEFAULT 0'),
            ('theme_accent', 'TEXT DEFAULT "cyan"')
        ]
        
        for col, typ in settings_cols:
            if col not in columns:
                print(f"Migrating: Adding '{col}' to user_settings.")
                cur.execute(f"ALTER TABLE user_settings ADD COLUMN {col} {typ}")
    except Exception as e:
        print(f"User settings migration failed: {e}")

    conn.commit()
    conn.close()
    print("Database initialized and checked.")
