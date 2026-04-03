import random
import csv
import os

def generate_large_dataset(num_rows=2000):
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
    
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Pune"]
    
    headers = ["name", "loan_amount", "status", "email", "tenure"]
    
    data = []
    for _ in range(num_rows):
        name = random.choice(names)
        # Adding some randomness to the name to avoid constant duplicates
        if random.random() > 0.3:
            name = f"{name} {random.randint(1, 100)}"
            
        loan_amount = random.randint(500, 20000) * 100 # 50,000 to 2,000,000
        
        # 80/20 split for Paid/Defaulted
        status = "Paid" if random.random() < 0.8 else "Defaulted"
        
        email = f"{name.lower().replace(' ', '.')}@example.com"
        tenure = random.choice([6, 12, 18, 24, 36, 48, 60])
        
        data.append([name, loan_amount, status, email, tenure])
        
    output_path = r"c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\data\kaggle_loan_dataset.csv"
    
    with open(output_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    
    print(f"Generated {num_rows} records at {output_path}")

if __name__ == "__main__":
    generate_large_dataset(2000)
