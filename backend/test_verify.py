import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError as e:
        print(f"Bcrypt failed with ValueError: {e}")
        return check_password_hash(hashed, password)

password = "Admin@123"
hashed = generate_password_hash(password)
print(f"Hashed (Werkzeug): {hashed}")

isValid = verify_password(password, hashed)
print(f"Is Valid: {isValid}")
