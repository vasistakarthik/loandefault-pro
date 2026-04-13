import os
from dotenv import load_dotenv

# Absolute path based loading which I implemented in the app
base_dir = os.path.dirname(os.path.abspath(__file__))
# The script is in scratch/, so the .env is one level up in loan_default_system/
env_path = os.path.join(base_dir, '..', '.env')
load_dotenv(dotenv_path=env_path)

print("--- SOVEREIGN ENVIRONMENT DIAGNOSTIC ---")
print(f"Project Path: {base_dir}")
print(f"APP_URL:      {os.environ.get('APP_URL')}")
print(f"PORT:         {os.environ.get('PORT')}")
print(f"DEBUG:        {os.environ.get('DEBUG')}")
print(f"ENV:          {os.environ.get('ENV')}")
print(f"LOG_LEVEL:    {os.environ.get('LOG_LEVEL')}")
print("--- DIAGNOSTIC COMPLETE ---")
