import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

import random
import string

def verify():
    s = requests.Session()
    
    rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    email = f"verify_{rand_suffix}@test.com"
    print(f"Using email: {email}")

    from bs4 import BeautifulSoup
    def get_csrf(url):
        res = s.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        token = soup.find('input', {'name': 'csrf_token'})
        return token['value'] if token else None

    # 1. Register
    print("1. Registering new user...")
    try:
        register_csrf = get_csrf(f"{BASE_URL}/register")
    except Exception:
        register_csrf = ""

    reg_data = {
        "name": "Verification User",
        "email": email,
        "password": "password123",
        "confirm_password": "password123",
        "csrf_token": register_csrf
    }
    r = s.post(f"{BASE_URL}/register", data=reg_data)
    
    # Successful registration redirects to login
    if "/login" in r.url:
        print("   Registration Successful (Redirected to Login).")
    else:
        print(f"   Registration Failed. URL: {r.url}")
        
    # 2. Login
    print("\n2. Logging in...")
    try:
        login_csrf = get_csrf(f"{BASE_URL}/login")
    except Exception:
        login_csrf = ""
    login_data = {
        "email": email,
        "password": "password123",
        "csrf_token": login_csrf
    }
    r = s.post(f"{BASE_URL}/login", data=login_data)
    
    if "/dashboard" in r.url:
        print("   Login Successful (Redirected to Dashboard).")
    else:
        print(f"   Login Failed. URL: {r.url}")
        print(f"   Note: This means authentication failed. Check database/hashing.")
        return

    # 3. Add Customer
    print(f"\n3. Adding Customer... to {BASE_URL}/add_customer")
    try:
        add_csrf = get_csrf(f"{BASE_URL}/add_customer")
    except Exception:
        add_csrf = ""
    customer_data = {
        "name": "API Test Customer",
        "age": 35,
        "income": 75000,
        "loan_amount": 20000,
        "credit_score": 720,
        "loan_type": "Personal Loan",
        "csrf_token": add_csrf
    }
    r = s.post(f"{BASE_URL}/add_customer", data=customer_data)
    
    if r.status_code == 200 and ("Risk Assessment" in r.text or "Prediction" in r.text or "risk-score" in r.text): 
         print("   Customer Added Successfully.")
    else:
         print(f"   Add Customer Failed: {r.status_code}")
         print(f"   Response URL: {r.url}")
         print(f"   Snippet: {r.text[:200]}...")

    # 4. Check Analytics
    print("\n4. Verifying Analytics API...")
    
    try:
        # Dashboard Trend
        r = s.get(f"{BASE_URL}/api/dashboard/trend")
        if r.status_code != 200:
            print(f"Trend API Failed: {r.status_code}")
            print(r.text[:200])
        else:
            print(f"   Dashboard Trend: {r.json()}")
        
        # Analytics Summary
        r = s.get(f"{BASE_URL}/api/analytics/summary")
        print(f"   Analytics Summary: {r.json()}")
        
    except Exception as e:
        print(f"JSON Error: {e}")
        print(f"Content was: {r.text[:200]}")
    
    # Recent Applications
    r = s.get(f"{BASE_URL}/api/applications?limit=5")
    print(f"   Recent Apps: {len(r.json()['applications'])} items returned.")

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"Verification Failed: {e}")
