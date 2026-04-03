import pandas as pd
import numpy as np
import random
import os

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_loan_dataset(num_records=15000):
    names = ["Aarav", "Aditya", "Amit", "Arjun", "Deepak", "Ishaan", "Karan", "Rahul", "Rohan", "Vikram",
             "Aadhya", "Anvi", "Diya", "Inaya", "Myra", "Nisha", "Pari", "Priya", "Saanvi", "Zara",
             "Michael", "Jessica", "David", "Jennifer", "James", "Robert", "Mary", "Patricia", "Linda", "Barbara"]
    
    last_names = ["Sharma", "Singh", "Joshi", "Verma", "Malhotra", "Nair", "Oberoi", "Mehra", "Sethi", "Khanna",
                  "Reddy", "Singh", "Sharma", "Murthy", "Patel", "Bhatia", "Gupta", "Das", "Iyer", "Nair",
                  "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

    employment_types = ['Salaried', 'Self-employed', 'Business', 'Government', 'Contract']
    loan_types = ['Personal Loan', 'Home Loan', 'Auto Loan', 'Business Loan', 'Education Loan']
    tenures = [6, 12, 18, 24, 36, 48, 60]
    
    data = []
    
    for _ in range(num_records):
        name = f"{random.choice(names)} {random.choice(last_names)}"
        if random.random() > 0.7:
            name += f" {random.randint(1, 100)}"
            
        age = random.randint(21, 70)
        credit_score = random.randint(300, 850)
        
        # Base annual income (centered around 6L)
        income = int(np.random.lognormal(mean=13.3, sigma=0.6))
        income = max(150000, min(10000000, income)) # Clamp between 1.5L and 1Cr
        
        # Loan amount requested
        loan_multiplier = random.uniform(0.2, 5.0)
        loan_amount = int(income * loan_multiplier)
        loan_amount = max(50000, min(10000000, loan_amount)) 
        
        emp_type = random.choice(employment_types)
        monthly_income = income / 12
        existing_emi = int(monthly_income * random.uniform(0, 0.4)) if random.random() > 0.4 else 0
        
        tenure = random.choice(tenures)
        loan_type = random.choice(loan_types)
        
        # --- Advanced Risk Model for higher predictivity ---
        # 1. Credit Risk (0.0 to 1.0)
        cs_factor = (850 - credit_score) / 550
        
        # 2. Leverage Risk (DTI)
        monthly_repayment = (loan_amount / tenure)
        total_monthly_obligation = existing_emi + monthly_repayment
        dti = total_monthly_obligation / (monthly_income + 1)
        dti_factor = min(1.5, dti) / 1.5 # Normalize to 1.0ish
        
        # 3. Income to Loan Risk (LTI)
        lti_factor = min(8.0, loan_amount / (income + 1)) / 8.0
        
        # 4. Employment Stability
        emp_risk = 0.4 if emp_type == 'Contract' else 0.2 if emp_type in ['Self-employed', 'Business'] else 0.05
        
        # Aggregate Risk Score with non-linear interactions
        # (e.g. High DTI + Low Credit Score = Dead certain default)
        aggregate_risk = (
            0.40 * cs_factor + 
            0.35 * dti_factor + 
            0.15 * lti_factor + 
            0.10 * emp_risk
        )
        
        # Bonus penalty for extreme DTI or very low Credit Score
        if dti > 0.6: aggregate_risk += 0.2
        if credit_score < 500: aggregate_risk += 0.15
        
        # Apply Sigmoid-like transformation to produce classes with clearer boundaries
        # Sharpness (steepness) makes it more "learnable"
        steepness = 12
        midpoint = 0.55
        prob = 1 / (1 + np.exp(-steepness * (aggregate_risk - midpoint)))
        
        # Add a tiny bit of noise (unpredictable life events)
        if random.random() < 0.05:
            status = random.choice(["Paid", "Defaulted"])
        else:
            status = "Defaulted" if random.random() < prob else "Paid"
        
        data.append({
            "Applicant Name": name,
            "Age": age,
            "Credit Score": credit_score,
            "Annual Income (₹)": income,
            "Requested Loan (₹)": loan_amount,
            "Employment Type": emp_type,
            "Existing Monthly EMI (₹)": existing_emi,
            "Loan Tenure (Months)": tenure,
            "Loan Type": loan_type,
            "Status": status
        })
    
    df = pd.DataFrame(data)
    
    # 1. Save detailed version for User (Kaggle Style)
    kaggle_path = os.path.join('data', 'kaggle_loan_dataset.csv')
    df.to_csv(kaggle_path, index=False)
    
    # 2. Save system version for training pipeline
    df_system = df.copy()
    df_system = df_system.rename(columns={
        "Applicant Name": "name",
        "Age": "age",
        "Annual Income (₹)": "income",
        "Requested Loan (₹)": "loan_amount",
        "Credit Score": "credit_score",
        "Employment Type": "employment_type",
        "Existing Monthly EMI (₹)": "existing_emi",
        "Loan Tenure (Months)": "tenure",
        "Loan Type": "loan_type",
        "Status": "default_status"
    })
    
    # Map Status string to 0/1
    df_system["default_status"] = df_system["default_status"].map({"Paid": 0, "Defaulted": 1})
    
    system_path = os.path.join('data', 'loan_dataset.csv')
    df_system.to_csv(system_path, index=False)
    
    print(f"Datasets generated successfully:")
    print(f" - Detailed: {kaggle_path}")
    print(f" - Train-ready: {system_path}")
    return kaggle_path

if __name__ == "__main__":
    generate_loan_dataset()
