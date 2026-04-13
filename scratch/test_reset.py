import requests
from bs4 import BeautifulSoup
import re

s = requests.Session()

# 1. Get CSRF token if any
try:
    r_get = s.get("http://127.0.0.1:5000/forgot-password")
    if r_get.status_code == 200:
        soup = BeautifulSoup(r_get.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        data = {'email': '2401600175mca@gmail.com'}
        if csrf_token:
            data['csrf_token'] = csrf_token['value']
        
        # 2. Trigger forgot password
        r_post = s.post("http://127.0.0.1:5000/forgot-password", data=data)
        print("Trigged forgot password. Status:", r_post.status_code)
    else:
        print("Server not running or route not found. Status:", r_get.status_code)
except Exception as e:
    print("Could not connect to server:", e)
