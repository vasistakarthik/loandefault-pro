import sqlite3
import time

conn = sqlite3.connect(r"c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db")
start = time.time()

active_count = conn.execute('''
    SELECT (SELECT COUNT(*) FROM loan_applications WHERE status IN ('Active', 'Approved')) +
           (SELECT COUNT(*) FROM loan_history WHERE status = 'Ongoing')
''').fetchone()[0]

pending_count = conn.execute("SELECT COUNT(*) FROM loan_applications WHERE status IN ('Pending', 'Under Review')").fetchone()[0]

defaulted_count = conn.execute('''
    SELECT (SELECT COUNT(*) FROM loan_applications WHERE status = 'Defaulted') +
           (SELECT COUNT(*) FROM loan_history WHERE status = 'Defaulted')
''').fetchone()[0]

print(f"KPI counts took: {time.time() - start:.4f}s")
conn.close()
