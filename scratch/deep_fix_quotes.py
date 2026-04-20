import os
import re

root_dir = r'c:\Users\Lenovo\OneDrive\Desktop\CLDRRP\loan_default_system\backend'
pattern = re.compile(r'status\s*=\s*"([^"]+)"')

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if pattern.search(content):
                new_content = pattern.sub(r"status = '\1'", content)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed quotes in: {filepath}")
