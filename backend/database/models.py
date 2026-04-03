from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_row):
        # Convert sqlite3.Row or dict to a standard dict for safe.get()
        data = dict(user_row) if hasattr(user_row, 'keys') else user_row
        
        self.id = data.get('id')
        self.name = data.get('name')
        self.email = data.get('email')
        self.password = data.get('password')
        self.role = data.get('role', 'analyst') or 'analyst'
        self._is_active = bool(data.get('is_active', True)) if data.get('is_active') is not None else True
        self.last_login = data.get('last_login')
        self.bank = data.get('bank', 'SBI')
        self.employee_id = data.get('employee_id', '')
        
    @property
    def is_active(self):
        return self._is_active
