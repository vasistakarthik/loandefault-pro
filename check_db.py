import sqlite3
import os

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables:", tables)
    cursor.execute('''
        SELECT 
            (SELECT COUNT(*) FROM loan_applications) + (SELECT COUNT(*) FROM customers) as total,
            (SELECT COUNT(*) FROM loan_applications WHERE risk_band = 'High Risk') + 
            (SELECT COUNT(*) FROM customers WHERE status = 'Defaulted') as high,
            (SELECT AVG(risk_probability) FROM customers) as avg_prob
    ''')
    res = cursor.fetchone()
    print("API Summary Query Result:", dict(zip(['total','high','avg_prob'], res)))
    conn.close()
