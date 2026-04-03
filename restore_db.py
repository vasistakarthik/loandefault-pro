import pandas as pd
import sqlite3
import os

db_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\database\loan.db'
csv_path = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\data\kaggle_loan_dataset.csv'

if not os.path.exists(csv_path):
    print("CSV not found, skipping db restoration.")
    exit(0)

conn = sqlite3.connect(db_path)
df = pd.read_csv(csv_path)

cur = conn.cursor()
updated = 0

for _, row in df.iterrows():
    name = row['Applicant Name']
    age = row['Age']
    cs = row['Credit Score']
    income = row['Annual Income (₹)']
    emp = row['Employment Type']
    loan_type = row['Loan Type']
    
    # Update loan_history
    cur.execute('''
        UPDATE loan_history 
        SET age = ?, credit_score = ?, annual_income = ?, employment_type = ?, loan_type = ?
        WHERE name = ? AND (age IS NULL OR credit_score IS NULL)
    ''', (age, cs, income, emp, loan_type, name))
    
    updated += cur.rowcount
    
    # Update borrowers table
    cur.execute('''
        UPDATE borrowers
        SET age = ?, credit_score = ?, annual_income = ?, employment_type = ?
        WHERE full_name = ? AND (age IS NULL OR credit_score IS NULL)
    ''', (age, cs, income, emp, name))

conn.commit()
conn.close()
print(f"Successfully backfilled demograpics for {updated} historical records.")
