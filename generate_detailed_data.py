import random
import csv
import os

def generate_large_detailed_dataset(num_rows=2000):
    names = [
        "Aarav Sharma", "Vivaan Gupta", "Aditya Singh", "Vihaan Patel", "Arjun Verma",
        "Sai Reddy", "Reyansh Kumar", "Aaryan Iyer", "Ishaan Nair", "Krishna Murthy",
        "Ananya Iyer", "Diya Sharma", "Pari Gupta", "Anvi Singh", "Myra Patel",
        "Aadhya Reddy", "Shanaya Kumar", "Saanvi Iyer", "Zara Nair", "Inaya Murthy",
        "Rahul Mehra", "Priya Das", "Amit Joshi", "Sonal Kapoor", "Deepak Malhotra",
        "Rohan Sethi", "Nisha Bhatia", "Vikram Khanna", "Shweta Aggarwal", "Karan Oberoi",
        "James Smith", "Michael Johnson", "Robert Williams", "David Brown", "Richard Taylor",
        "Emily Davis", "Sarah Miller", "Jessica Wilson", "Ashley Moore", "Jennifer Taylor"
    ]
    
    default_reasons = [
        "Unemployment / Job Loss", "Medical Emergency / High Bills", 
        "Business Multi-sector Failure", "High Debt Consolidation",
        "Personal/Family Crisis", "Interest Rate Overrun", "N/A"
    ]
    
    headers = [
        "id", "name", "email", "loan_amount", "paid_amount", 
        "balance_amount", "status", "tenure", "months_completed", "default_reason"
    ]
    
    data = []
    for i in range(1, num_rows + 1):
        name = random.choice(names)
        if random.random() > 0.4:
            name = f"{name} {random.randint(100, 999)}"
            
        loan_amount = random.randint(100, 20000) * 100 # 10,000 to 2,000,000
        tenure = random.choice([12, 24, 36, 48, 60])
        
        # Determine status
        rand_val = random.random()
        if rand_val < 0.70:
            status = "Paid"
            months_completed = tenure
            paid_amount = loan_amount
            balance_amount = 0
            reason = "N/A"
        elif rand_val < 0.85:
            status = "Ongoing"
            months_completed = random.randint(1, tenure - 1)
            paid_amount = round((loan_amount / tenure) * months_completed, 2)
            balance_amount = loan_amount - paid_amount
            reason = "N/A"
        else:
            status = "Defaulted"
            months_completed = random.randint(1, tenure // 2) # Usually default early
            paid_amount = round((loan_amount / tenure) * months_completed * 0.8, 2) # Some penalty or missed payments
            balance_amount = loan_amount - paid_amount
            reason = random.choice(default_reasons[:-1])
        
        email = f"{name.lower().replace(' ', '.')}@bank.com"
        
        data.append([
            i, name, email, loan_amount, paid_amount, 
            balance_amount, status, tenure, months_completed, reason
        ])
        
    output_path = r"c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\data\bank_detailed_history.csv"
    
    with open(output_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    print(f"Generated {num_rows} detailed records at {output_path}")

if __name__ == "__main__":
    generate_large_detailed_dataset(2000)
