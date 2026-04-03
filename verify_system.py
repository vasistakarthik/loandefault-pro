import os
import sys
import sqlite3
import json
import pickle

def verify_system():
    print("--- Institutional Node Verification ---")
    
    # 1. Database Check
    db_path = r'backend/database/loan.db'
    if not os.path.exists(db_path):
        print("[FAIL] Database node MISSING.")
    else:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]
            print(f"[OK] Database connection established. Tables identified: {len(tables)}")
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"[OK] Persistence unit active: {user_count} Identity Nodes (Users) found.")
            conn.close()
        except Exception as e:
            print(f"[FAIL] Database connection error: {e}")

    # 2. Intelligence Unit (Model) Check
    model_dir = 'backend/model'
    model_path = os.path.join(model_dir, 'risk_model.pkl')
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            # Use type() instead of __name__ directly to be safe
            print(f"[OK] Intelligence model (XGBoost/Pipeline) loaded: {type(model)}")
        except Exception as e:
            print(f"[FAIL] Model extraction failure. Error Code: {e}")
    else:
        print("[WARNING] Risk Model node (risk_model.pkl) missing from expected quadrant.")

    # 3. Frontend Node Integrity
    templates = [
        'dashboard.html',
        'reports.html',
        'login.html',
        'register.html',
        'historical_network.html',
        'model_performance.html'
    ]
    missing = 0
    for t in templates:
        p = os.path.join('frontend/templates', t)
        if not os.path.exists(p):
            print(f"[FAIL] Missing Template: {t}")
            missing += 1
    if missing == 0:
        print(f"[OK] All {len(templates)} display templates verified.")

    # 4. Neural Network (Dependencies)
    try:
        import flask
        import pandas
        import xgboost
        import shap
        import bcrypt
        print("[OK] Strategic software dependencies (Flask, Pandas, XGBoost, SHAP, Bcrypt) verified.")
    except ImportError as e:
        print(f"[FAIL] Critical dependency failure: {e}")

    print("--- Verification Complete ---")

if __name__ == "__main__":
    verify_system()
