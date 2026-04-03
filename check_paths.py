import os
import sys

# Simulate what app.py does
base_dir = os.path.dirname(os.path.abspath('backend/app.py'))
template_dir = os.path.normpath(os.path.join(base_dir, '..', 'frontend', 'templates'))
print(f"Flask Template Dir: {template_dir}")
print(f"File exists: {os.path.exists(os.path.join(template_dir, 'index.html'))}")
