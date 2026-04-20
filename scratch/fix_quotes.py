import os

filepath = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend\routes\customer_routes.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences of status = "..." with status = '...'
import re
# Pattern to find status = "..." where " is double quote
new_content = re.sub(r'status\s*=\s*"([^"]+)"', r"status = '\1'", content)

if new_content != content:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Replacements made.")
else:
    print("No replacements found.")
