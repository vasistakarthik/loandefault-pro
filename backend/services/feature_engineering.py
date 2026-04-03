import numpy as np

def calculate_historical_risk(user_loans):
    """
    Calculates historical loan behavior risk score.
    Returns value between 0 and 1.
    """

    if not user_loans:
        return 0.2  # Neutral baseline for new users

    total_loans = len(user_loans)
    # Adapting to schema: status == 'Defaulted' means is_default
    defaults = sum(1 for loan in user_loans if loan['status'] == 'Defaulted')
    # Adapting to schema: loan_amount
    avg_amount = sum(loan['loan_amount'] for loan in user_loans) / total_loans

    default_ratio = defaults / total_loans

    # Normalize avg amount (adjust if needed): Based on 1,000,000 as max normalization
    normalized_amount = min(avg_amount / 1000000, 1)

    historical_score = (0.7 * default_ratio) + (0.3 * normalized_amount)

    return min(historical_score, 1)

def prepare_features(df):
    """
    Standardized feature engineering for both training and inference.
    """
    # Create copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Core Ratios
    df['monthly_income'] = df['income'] / 12
    df['monthly_emi'] = df['loan_amount'] / df['tenure']
    
    # Debt-to-Income (DTI) - Professional variant
    df['dti'] = (df['existing_emi'] + df['monthly_emi']) / (df['monthly_income'] + 1)
    
    # Loan-to-Income (LTI)
    df['lti'] = df['loan_amount'] / (df['income'] + 1)
    
    # Financial Stability Metrics
    df['payment_capacity'] = df['monthly_income'] - (df['existing_emi'] + df['monthly_emi'])
    df['disposable_income_ratio'] = df['payment_capacity'] / (df['monthly_income'] + 1)
    
    # Risk Factor Interactions
    df['credit_utilization_proxy'] = df['loan_amount'] / (df['credit_score'] * 100 + 1)
    df['risk_multiplier'] = (1000 - df['credit_score']) * df['lti']
    df['age_risk_factor'] = df['age'] * (850 - df['credit_score']) / 100
    
    # Advanced Banking Ratios
    df['income_to_loan_ratio'] = df['income'] / (df['loan_amount'] + 1)
    df['debt_service_ratio'] = (df['existing_emi'] * 12) / (df['income'] + 1)
    df['score_income_index'] = (df['credit_score'] * np.log1p(df['income'])) / 100
    
    # Critical Interaction Terms
    df['score_lti_interaction'] = df['credit_score'] * df['lti']
    df['income_tenure_factor'] = (df['income'] / 100000) * df['tenure']
    
    # Non-linear transformations
    df['log_income'] = df['income'].apply(lambda x: np.log1p(max(0, x)))
    df['debt_pressure'] = df['existing_emi'] / (df['income'] + 1)
    
    return df
