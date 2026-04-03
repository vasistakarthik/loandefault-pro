
import requests
import time

URL = "http://127.0.0.1:5000/debug_db"

print("Waiting for server...")
time.sleep(2)

print("\n--- BYPASS AUTH DEBUG CHECK ---")
try:
    resp = requests.get(URL)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
