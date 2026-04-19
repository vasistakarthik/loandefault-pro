import sqlite3
import os
from dotenv import load_dotenv

# Find the project root (one level up from the 'backend/database' folder)
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '..', '..', '.env')
load_dotenv(dotenv_path=env_path)

def get_db_connection():
    # Use current_app config if available (within Flask context)
    try:
        from flask import current_app
        db_path = current_app.config['DATABASE_URI']
    except (ImportError, RuntimeError):
        # Fallback for scripts outside Flask context
        db_path = os.environ.get('DATABASE_URL')
        if not db_path:
            BASE_DIR = os.path.abspath(os.path.dirname(__file__))
            db_path = os.path.join(BASE_DIR, 'loan.db')
    
    # Handle PostgreSQL
    if db_path.startswith('postgres://') or db_path.startswith('postgresql://'):
        import psycopg2
        from psycopg2.extras import DictCursor
        
        # fix Render/Heroku postgres:// vs postgresql://
        if db_path.startswith("postgres://"):
            db_path = db_path.replace("postgres://", "postgresql://", 1)
            
        conn = psycopg2.connect(db_path)
        
        # Wrapper to make Postgres connection behave like SQLite connection
        class PostgresWrapper:
            def __init__(self, conn):
                self.conn = conn
            
            def execute(self, sql, params=None):
                # Convert '?' to '%s' for Postgres
                if params and isinstance(sql, str):
                    sql = sql.replace('?', '%s')
                cur = self.conn.cursor(cursor_factory=DictCursor)
                cur.execute(sql, params)
                return cur
            
            def executescript(self, sql):
                # Postgres doesn't have executescript, just use execute
                cur = self.conn.cursor()
                cur.execute(sql)
                return cur

            def commit(self):
                self.conn.commit()
                
            def rollback(self):
                self.conn.rollback()
                
            def close(self):
                self.conn.close()
                
            def cursor(self):
                cur = self.conn.cursor(cursor_factory=DictCursor)
                # Monkeypatch to support fetchall/fetchone directly on cursor
                return cur

            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type:
                    self.conn.rollback()
                else:
                    self.conn.commit()
                self.conn.close()

        return PostgresWrapper(conn)

    # Handle SQLite
    if db_path.startswith('sqlite://'):
        db_path = db_path.replace('sqlite:///', '')
    
    conn = sqlite3.connect(db_path, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 20000")
    return conn


def init_db():
    conn = get_db_connection()
    is_postgres = hasattr(conn, 'conn') # Check if it's our wrapper
    
    # 1. Create tables if they don't exist (using schema.sql)
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        
        if is_postgres:
            # Basic conversions for schema compatibility
            schema_sql = schema_sql.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
            schema_sql = schema_sql.replace('DATETIME', 'TIMESTAMP')
            schema_sql = schema_sql.replace('REAL', 'DOUBLE PRECISION')
            # Postgres doesn't need executescript for multiple statements usually, but we need to handle it
            cur = conn.conn.cursor()
            cur.execute(schema_sql)
            conn.conn.commit()
        else:
            conn.executescript(schema_sql)
    
    # 2. Check for missing columns (Migration logic)
    cur = conn.cursor()
    
    def column_exists(table, column):
        if is_postgres:
            cur.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name=%s AND column_name=%s",
                (table, column)
            )
            return cur.fetchone() is not None
        else:
            cur.execute(f"PRAGMA table_info({table})")
            columns = [info[1] for info in cur.fetchall()]
            return column in columns

    def add_column(table, column, type_def):
        if not column_exists(table, column):
            print(f"Migrating: Adding '{column}' to {table}.")
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")

    # Migration checks
    add_column('users', 'role', "TEXT DEFAULT 'analyst'")
    add_column('users', 'created_at', "TIMESTAMP")
    add_column('users', 'is_active', "INTEGER DEFAULT 1")
    add_column('users', 'last_login', "TIMESTAMP")
    add_column('users', 'verification_token', "TEXT")
    add_column('users', 'is_verified', "INTEGER DEFAULT 1")
    add_column('users', 'employee_id', "TEXT")
    add_column('users', 'bank', "TEXT DEFAULT 'SBI'")

    add_column('customers', 'loan_type', "TEXT")
    add_column('customers', 'risk_reason', "TEXT")
    add_column('customers', 'prediction_result', "TEXT")
    add_column('customers', 'risk_probability', "DOUBLE PRECISION")
    add_column('customers', 'existing_emi', "DOUBLE PRECISION DEFAULT 0")
    add_column('customers', 'employment_type', "TEXT DEFAULT 'Salaried'")
    add_column('customers', 'tenure', "INTEGER DEFAULT 12")
    add_column('customers', 'status', "TEXT DEFAULT 'Pending'")
    add_column('customers', 'record_hash', "TEXT")

    add_column('loan_history', 'paid_amount', "DOUBLE PRECISION DEFAULT 0")
    add_column('loan_history', 'balance_amount', "DOUBLE PRECISION DEFAULT 0")
    add_column('loan_history', 'months_completed', "INTEGER DEFAULT 0")
    add_column('loan_history', 'default_reason', "TEXT")
    add_column('loan_history', 'import_batch', "TEXT")
    add_column('loan_history', 'age', "INTEGER")
    add_column('loan_history', 'credit_score', "INTEGER")
    add_column('loan_history', 'annual_income', "DOUBLE PRECISION")
    add_column('loan_history', 'employment_type', "TEXT DEFAULT 'Salaried'")
    add_column('loan_history', 'loan_type', "TEXT DEFAULT 'Personal Loan'")
    add_column('loan_history', 'existing_emi', "DOUBLE PRECISION DEFAULT 0")
    add_column('loan_history', 'risk_score', "DOUBLE PRECISION")
    add_column('loan_history', 'borrower_id', "INTEGER")
    add_column('loan_history', 'physical_address', "TEXT")
    add_column('loan_history', 'contact_phone', "TEXT")

    add_column('model_registry', 'path', "TEXT")
    add_column('model_registry', 'is_active', "INTEGER DEFAULT 0")
    add_column('model_registry', 'f1_score', "DOUBLE PRECISION")
    add_column('model_registry', 'metadata', "TEXT")

    add_column('borrowers', 'status', "TEXT DEFAULT 'Pending'")
    add_column('borrowers', 'creation_source', "TEXT DEFAULT 'Manual'")
    add_column('borrowers', 'physical_address', "TEXT")
    add_column('borrowers', 'contact_phone', "TEXT")
    add_column('borrowers', 'paid_amount', "DOUBLE PRECISION DEFAULT 0")
    add_column('borrowers', 'balance_amount', "DOUBLE PRECISION DEFAULT 0")
    add_column('borrowers', 'bank', "TEXT DEFAULT 'SBI'")

    # Governance columns for audit_logs
    for col in ['user_id', 'user_email', 'ip_address', 'borrower_email', 'model_version', 'risk_level', 'input_data', 'shap_explanation']:
        add_column('audit_logs', col, "TEXT" if col != 'user_id' else "INTEGER")

    # Thresholds for user_settings
    for col, typ in [('low_threshold', 'INTEGER DEFAULT 40'), ('med_threshold', 'INTEGER DEFAULT 70'), ('theme_accent', 'TEXT DEFAULT "cyan"')]:
        add_column('user_settings', col, typ)

    conn.commit()
    conn.close()
    print("Database initialized and checked.")
