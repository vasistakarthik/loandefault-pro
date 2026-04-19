CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'analyst',
    is_active INTEGER DEFAULT 1,
    is_verified INTEGER DEFAULT 0,
    verification_token TEXT,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    bank TEXT DEFAULT 'SBI',
    employee_id TEXT
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    income REAL,
    loan_amount REAL,
    credit_score INTEGER,
    prediction_result TEXT,
    risk_probability REAL,
    risk_reason TEXT,
    loan_type TEXT,
    existing_emi REAL DEFAULT 0,
    employment_type TEXT DEFAULT 'Salaried',
    tenure INTEGER DEFAULT 12,
    interest_rate REAL,
    bank TEXT,
    record_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL,
    accuracy REAL,
    precision_score REAL,
    recall_score REAL,
    f1_score REAL,
    roc_auc REAL,
    is_active INTEGER DEFAULT 0,
    trained_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT -- JSON string for additional metrics/hyperparameters
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    action TEXT,
    borrower_email TEXT,
    model_version TEXT,
    risk_level TEXT,
    user_id INTEGER,
    ip_address TEXT,
    input_data TEXT, -- JSON string of features used
    shap_explanation TEXT, -- JSON string of SHAP values
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    loan_amount REAL NOT NULL,
    paid_amount REAL DEFAULT 0,
    balance_amount REAL DEFAULT 0,
    status TEXT, -- 'Paid', 'Defaulted', 'Ongoing'
    tenure INTEGER,
    months_completed INTEGER DEFAULT 0,
    default_reason TEXT, -- e.g., 'Job Loss', 'Medical', 'Business Failure'
    risk_score REAL, -- Added for enterprise risk tracking
    borrower_id INTEGER, -- Added for enterprise risk tracking
    import_batch TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    dark_mode INTEGER DEFAULT 1,
    theme_accent TEXT DEFAULT 'cyan',
    email_notifications INTEGER DEFAULT 1,
    risk_threshold INTEGER DEFAULT 80,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS borrowers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    age INTEGER,
    email TEXT,
    credit_score INTEGER,
    annual_income REAL,
    employment_type TEXT,
    bank TEXT DEFAULT 'SBI',
    physical_address TEXT,
    contact_phone TEXT,
    paid_amount REAL DEFAULT 0,
    balance_amount REAL DEFAULT 0,
    creation_source TEXT DEFAULT 'Manual',
    status TEXT DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS loan_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    borrower_id INTEGER,
    loan_amount REAL,
    tenure_months INTEGER,
    interest_rate REAL,
    emi REAL,
    risk_band TEXT,
    status TEXT,
    record_hash TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (borrower_id) REFERENCES borrowers(id)
);


