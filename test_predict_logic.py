from backend.model.predict import predict

# Test Cases
test_profiles = [
    {
        "name": "Perfect Borrower",
        "age": 40, "income": 2000000, "loan_amount": 500000, 
        "credit_score": 820, "loan_type": "Home Loan", "existing_emi": 10000, 
        "employment_type": "Government", "tenure": 60
    },
    {
        "name": "Risky Borrower",
        "age": 22, "income": 300000, "loan_amount": 800000, 
        "credit_score": 550, "loan_type": "Personal Loan", "existing_emi": 15000, 
        "employment_type": "Contract", "tenure": 12
    }
]

print("--- PREDICTION ENGINE TEST ---\n")
for p in test_profiles:
    res, reason, prob, _, breakdown = predict(
        p['age'], p['income'], p['loan_amount'], p['credit_score'], 
        p['loan_type'], p['name'], p['existing_emi'], p['employment_type'], p['tenure']
    )
    print(f"Name: {p['name']}")
    print(f"  Result: {res}")
    print(f"  Probability: {round(prob * 100, 2)}%")
    print(f"  Breakdown: {breakdown}")
    print("-" * 30)
