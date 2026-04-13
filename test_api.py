import requests
import os
from dotenv import load_dotenv

# Find the project root (current folder)
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_path)

BASE_URL = os.environ.get("APP_URL", 'http://localhost:5000')

def test_endpoint(name, path):
    try:
        r = requests.get(f'{BASE_URL}{path}', timeout=2)
        # Most of these require login, so 302/401 is actually a "Connection Success" if the server responds
        status = r.status_code
        if status in [200, 302, 401, 403]:
            print(f"[OK] {name}: {status} (Node Responding)")
        else:
            print(f"[FAIL] {name}: {status} (Node Error)")
    except Exception as e:
        print(f"[ERROR] {name}: {e}")

if __name__ == "__main__":
    print("--- Probing Infrastructure Nodes ---")
    test_endpoint("Institutional Portal", "/login")
    test_endpoint("Dashboard Telemetry", "/api/dashboard/stats")
    test_endpoint("Model Metrics HUD", "/api/model/metrics")
    test_endpoint("Audit Feed Stream", "/api/dashboard/audit-feed")
