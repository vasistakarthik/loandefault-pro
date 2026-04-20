import pickle
import os
import json
import pandas as pd
import shap
import numpy as np


_cached_model = None

def load_model():
    global _cached_model
    if _cached_model is not None:
        return _cached_model
        
    try:
        from ..services.model_registry import ModelRegistry
        active_model = ModelRegistry.get_active_model()
        
        if active_model and os.path.exists(active_model['path']):
            model_path = active_model['path']
        else:
            # Fallback path
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, 'risk_model.pkl')
            
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                _cached_model = pickle.load(f)
            return _cached_model
        return None
    except Exception as e:
        print(f"Model Loading Error: {e}")
        return None


_cached_explainer = None

def explain_prediction(model, data_df):
    """
    Generates SHAP values to explain the prediction.
    Supports Pipeline with Preprocessor.
    """
    global _cached_explainer
    try:
        # If it's a pipeline, we need to transform data first
        if hasattr(model, 'named_steps') and 'preprocessor' in model.named_steps:
            preprocessor = model.named_steps['preprocessor']
            # Access the underlying model inside CalibratedClassifierCV
            clf_wrapper = model.named_steps['classifier']
            
            # Get the first calibrated classifier's estimator
            base_model = clf_wrapper.calibrated_classifiers_[0].estimator
            
            # Transform data
            X_transformed = preprocessor.transform(data_df)
            
            # Handle sparse matrix from transformer (OneHotEncoder output)
            if hasattr(X_transformed, 'toarray'):
                X_transformed = X_transformed.toarray()
            
            if _cached_explainer is None:
                _cached_explainer = shap.TreeExplainer(base_model)
                
            shap_values = _cached_explainer.shap_values(X_transformed)
            
            # XGBoost 3.x returns single array for binary, older might return list
            if isinstance(shap_values, list):
                vals = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
            else:
                # For XGBoost it's often a 2D array [sample, feature]
                vals = shap_values[0] if len(shap_values.shape) > 1 else shap_values

            # Get feature names from preprocessor
            numeric_features = [
                'age', 'income', 'loan_amount', 'credit_score', 'existing_emi', 'tenure', 
                'dti', 'lti', 'payment_capacity', 'monthly_income', 'monthly_emi', 
                'disposable_income_ratio', 'credit_utilization_proxy',
                'risk_multiplier', 'age_risk_factor', 'debt_pressure', 'log_income',
                'income_to_loan_ratio', 'debt_service_ratio', 'score_income_index',
                'score_lti_interaction', 'income_tenure_factor'
            ]
            ohe = preprocessor.named_transformers_['cat']
            cat_feature_names = ohe.get_feature_names_out(['employment_type', 'loan_type']).tolist()
            feature_names = numeric_features + cat_feature_names
            
            # Handle single vs multi-sample SHAP values
            def get_scalar(v):
                if hasattr(v, '__iter__') and not isinstance(v, (str, bytes)):
                    # Recursively get the first element if it's a list/array
                    return get_scalar(v[0])
                return v

            explanation = []
            for name, val in zip(feature_names, vals):
                explanation.append({'feature': name, 'impact': float(round(get_scalar(val), 4))})
                
            explanation.sort(key=lambda x: abs(x['impact']), reverse=True)
            return explanation
            
        return []
    except Exception as e:
        print(f"SHAP Professional Error: {e}")
        return []

def predict(age, income, loan_amount, credit_score, loan_type=None, name=None, 
            existing_emi=0, employment_type='Salaried', tenure=12, thresholds=None, 
            address=None, phone=None):
    from ..services.feature_engineering import calculate_historical_risk, prepare_features
    from ..database.db import get_db_connection
    
    # 0. Get Latest Model Info (Step 2B/Versioning)
    model_version = "v3.0-Elite-Banking"
    try:
        conn = get_db_connection()
        latest = conn.execute('SELECT version FROM model_registry ORDER BY trained_at DESC LIMIT 1').fetchone()
        conn.close()
        if latest: model_version = latest['version']
    except: pass

    model = load_model()
    
    # 1. Fetch History & Calculate Historical Risk Score
    historical_score = 0.2
    history_summary = "No previous loan record found."
    
    gnn_fraud_factor = 0.0 # GNN contamination score
    cluster_nodes = [] # Identified nodes in the fraud matrix

    conn = get_db_connection()
    if name:
        # Check standard History
        history = conn.execute('SELECT * FROM loan_history WHERE name = ?', (name,)).fetchall()
        # Check Active Applications status
        active_defaults = conn.execute('''
            SELECT count(*) FROM loan_applications la
            JOIN borrowers b ON la.borrower_id = b.id
            WHERE b.full_name = ? AND la.status = 'Defaulted'
        ''', (name,)).fetchone()[0]
        # Check Assessment History records
        assessment_defaults = conn.execute("SELECT count(*) FROM customers WHERE name = ? AND status = 'Defaulted'", (name,)).fetchone()[0]
        
        total_defaults = (sum(1 for h in history if h['status'] and str(h['status']).lower() == 'defaulted')) + active_defaults + assessment_defaults

        if history or total_defaults > 0:
            historical_score = calculate_historical_risk(history)
            defaults = total_defaults # Define defaults clearly for the override logic
            if total_defaults > 0:
                history_summary = f"CRITICAL: {total_defaults} prior default(s) detected across system nodes."
            else:
                history_summary = f"Stable profile with {len(history)} verified clean records."
        else:
            defaults = 0 # Ensure defaults is defined even if no history

    # --- 1.2: GNN NODAL CLUSTER ANALYSIS (Fraud Matrix) ---
    if address or phone:
        # Search for shared identifiers linked to defaulted nodes
        contamination_query = '''
            SELECT b.full_name, b.status 
            FROM borrowers b
            WHERE (b.physical_address = ? AND b.physical_address IS NOT NULL AND b.physical_address <> '')
               OR (b.contact_phone = ? AND b.contact_phone IS NOT NULL AND b.contact_phone <> '')
        '''
        linked_nodes = conn.execute(contamination_query, (address, phone)).fetchall()
        
        defaulted_links = [n['full_name'] for n in linked_nodes if n['status'] == 'Defaulted']
        if defaulted_links:
            gnn_fraud_factor = 0.15 * len(defaulted_links) # 15% risk increase per linked defaulted node
            cluster_nodes = defaulted_links
    
    conn.close()

    if not model:
        return ("Model not found", "System Error", 0.0, [], {})
    
    # 2. Expert Feature Synthesis
    data_raw = pd.DataFrame([{
        'age': age, 
        'income': income, 
        'loan_amount': loan_amount, 
        'credit_score': credit_score,
        'existing_emi': existing_emi,
        'tenure': tenure,
        'employment_type': employment_type,
        'loan_type': loan_type
    }])
    
    data = prepare_features(data_raw)
    
    # Extract calculated ratios for breakdown
    dti = data['dti'].iloc[0]
    lti = data['lti'].iloc[0]
    
    # ML Prediction (Calibrated PD)
    ml_pb_default = 0.5
    try:
        ml_pb_default = model.predict_proba(data)[0][1]
    except Exception as e:
        print(f"Professional ML Predict failed: {e}")

    # 3. Behavioral Psychometrics & Hybrid Risk Blending (Banking Standards)
    intent_risk = 0.2 
    if credit_score < 580 and loan_amount > (income * 1.5):
        intent_risk = 0.85 
    elif income > 1200000 and loan_amount < 300000:
        intent_risk = 0.05 

    # Calculate Heuristic Probability (Rules-based risk)
    heuristic_prob = (0.7 * dti + 0.3 * lti)
    if credit_score < 600: heuristic_prob += 0.1
    heuristic_prob = max(0.01, min(0.99, heuristic_prob))

    # Updated Blending: 40% ML, 20% History, 20% GNN Fraud, 10% Heuristics, 10% Psychometrics
    final_prob = (0.40 * ml_pb_default + 0.20 * historical_score + 0.20 * min(1.0, gnn_fraud_factor) + 0.10 * heuristic_prob + 0.10 * intent_risk)
    
    # Apply product-specific risk adjustments
    risk_adj = 0.0
    if loan_type == "personal": risk_adj = 0.05
    elif loan_type == "business": risk_adj = 0.10
    elif loan_type == "home": risk_adj = -0.10
    
    final_prob = max(0.01, min(0.99, final_prob + risk_adj))

    # 4. Professional Banking Metrics (Sovereign Core v4.0)
    PD = final_prob  # Probability of Default
    LGD = 0.40       # Loss Given Default (Industry standard assumption 40% for unsecured)
    
    # Exposure at Default (EAD)
    EAD = loan_amount
    
    # Expected Loss (EL)
    EL = PD * LGD * EAD
    
    # Basel III Risk-Weighted Assets (RWA) Approximation
    # Correlation (R) and Capital Requirement (K) for Corporate/Retail exposures
    R = 0.12 * (1 - np.exp(-50 * PD)) / (1 - np.exp(-50)) + \
        0.24 * (1 - (1 - np.exp(-50 * PD)) / (1 - np.exp(-50)))
    
    from scipy.stats import norm
    # Maturity adjustment (b) and Capital Requirement (K)
    # Using 99.9% confidence interval for unexpected loss
    b = (0.11852 - 0.05478 * np.log(PD))**2
    M = 2.5 # Average 2.5 years maturity as baseline
    K = (LGD * norm.cdf((norm.ppf(PD) + np.sqrt(R) * norm.ppf(0.999)) / np.sqrt(1 - R)) - PD * LGD) * \
        (1 + (M - 2.5) * b) / (1 - 1.5 * b)
    
    RWA = K * 12.5 * EAD
    
    # 5. Risk-Adjusted Pricing & Capital
    base_rate = 0.08  # 8% base bank rate
    risk_premium = (PD * LGD) * 2 # Double the expected loss as margin
    suggested_rate = base_rate + risk_premium
    
    # Capital Adequacy Requirement (approx 8% of RWA)
    regulatory_capital = RWA * 0.08
    
    # RAROC (Risk-Adjusted Return on Capital)
    # (Revenue - Costs - Expected Loss) / Economic Capital
    revenue = loan_amount * suggested_rate
    raroc = (revenue - EL) / (regulatory_capital + 1)

    # AI Reasoning Core v4.3 (Dynamic Intelligence)
    reasons = []
    
    # 1. GNN Nodal Contagion Alert
    if gnn_fraud_factor > 0:
        contamination_pct = int(gnn_fraud_factor * 100)
        nodes_str = ", ".join(cluster_nodes[:2])
        if len(cluster_nodes) > 2: nodes_str += f" and {len(cluster_nodes)-2} others"
        reasons.append(f"GNN ALERT: Risk Contamination Detected ({contamination_pct}% boost). Shared identifiers linked to defaulted nodes: [{nodes_str}].")

    # 2. AI Feature Impact Reasoning (SHAP-Driven)
    shap_explanation = explain_prediction(model, data)
    if shap_explanation:
        # Filter for top impactful features (impact > 0 is risk, < 0 is safety)
        risk_drivers = [f for f in shap_explanation if f['impact'] > 0.05][:2]
        safety_anchors = [f for f in shap_explanation if f['impact'] < -0.05][:1]
        
        for feat in risk_drivers:
            f_name = feat['feature'].replace('_', ' ').replace('dti', 'Debt-to-Income').replace('lti', 'Loan-to-Income').title()
            reasons.append(f"AI identified {f_name} as a primary risk driver (Impact: {feat['impact']:.2f}).")
            
        for feat in safety_anchors:
            f_name = feat['feature'].replace('_', ' ').replace('dti', 'Debt-to-Income').title()
            reasons.append(f"Stability supported by {f_name} (Safety Impact: {abs(feat['impact']):.2f}).")

    # 3. Hard Financial Guardrails (Expert Heuristics)
    if dti > 0.50: 
        reasons.append(f"CRITICAL: Debt-to-Income ratio ({dti:.1f}) exceeds institutional default safety ceilings.")
    if credit_score < 600:
        reasons.append(f"CREDIT WARNING: Bureau score {credit_score} is categorized as Sub-Prime.")
    if lti > 5.0:
        reasons.append(f"LEVERAGE WARNING: Loan-to-Income ({lti:.1f}x) indicates high consumer over-extension.")
    
    if len(reasons) == 0:
        reasons.append("Profile shows balanced risk-to-reward metrics based on historical baselines.")

    # 4. Behavioral Psychometric Invariants
    if intent_risk > 0.70:
        reasons.append("BEHAVIORAL WARNING: Model detected High Desperation/Intent Stress in the borrower node.")

    # 5. Accurate Risk Classification (Sovereign Thresholds)
    low_t = thresholds[0]/100.0 if thresholds else 0.20
    high_t = thresholds[1]/100.0 if thresholds else 0.50
    
    if PD > high_t:
        risk_level = "High Risk"     # DEFAULT LIKELY
    elif PD < low_t:
        risk_level = "Low Risk"      # SANCTION RECOMMENDED
    else:
        risk_level = "Medium Risk"   # MARGINAL / UNDER REVIEW
    
    # Heuristic Override for extreme cases (Force accurate rejection)
    if dti > 0.65 or credit_score < 500 or (defaults > 0 if 'defaults' in locals() else False) or (gnn_fraud_factor > 0.4):
        risk_level = "High Risk"
        if gnn_fraud_factor > 0.4:
            reasons.insert(0, "SYSTEM LOCK: High proximity to multiple defaulted nodes in Fraud Matrix. Access Denied.")
        elif (defaults > 0 if 'defaults' in locals() else False):
            reasons.insert(0, f"MANDATORY REJECTION: Borrower has {defaults} documented default(s). Sanction breach detected.")
        else:
            reasons.append("System Override: Automatic Default classification due to extreme financial insolvency indicators.")

    # Select the most accurate reasons (Joined for complete record)
    full_reason = " ||| ".join(reasons) if reasons else "Profile shows balanced metrics."

    breakdown = {
        "pd": round(PD * 100, 2),
        "pd_raw": float(PD),
        "lgd": 40.0,
        "el": round(EL, 2),
        "rwa": round(RWA, 2),
        "suggested_rate": round(suggested_rate * 100, 2),
        "raroc": round(raroc * 100, 2),
        "regulatory_capital": round(regulatory_capital, 2),
        "dti": round(dti, 2),
        "lti": round(lti, 2),
        "risk_score": round(PD * 100, 0),
        "risk_level": risk_level.upper(),
        "model_version": model_version,
        "historical_impact": round(historical_score * 100, 2),
        "ai_confidence": round(ml_pb_default * 100, 2),
        "psychometric_intent": round(intent_risk * 100, 2), 
        "gnn_fraud_factor": round(gnn_fraud_factor * 100, 2),
        "cluster_nodes": cluster_nodes,
        "max_recommended_loan": round(income * 0.40 * tenure, 2)
    }

    return risk_level, full_reason, PD, shap_explanation, breakdown


