import pandas as pd
import numpy as np
import pickle
import os
import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, VotingClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from ..database.db import init_db
from ..services.feature_engineering import prepare_features

from imblearn.combine import SMOTETomek
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.preprocessing import PolynomialFeatures

def train():
    try:
        print("Starting model training (XGBoost v4.0)...")
        # Ensure database is up-to-date with migrations
        init_db()
        
        base_dir = os.path.dirname(os.path.abspath(__file__))

        data_path = os.path.join(base_dir, '..', '..', 'data', 'loan_dataset.csv')
        
        if not os.path.exists(data_path):
            return {'success': False, 'message': "Training data source missing."}
        
        df = pd.read_csv(data_path)
        
        # 1. Advanced Centralized Feature Engineering
        print("Performing feature engineering...")
        df = prepare_features(df)
        
        # 2. Pipeline Configuration
        numeric_features = [
            'age', 'income', 'loan_amount', 'credit_score', 'existing_emi', 'tenure', 
            'dti', 'lti', 'payment_capacity', 'monthly_income', 'monthly_emi', 
            'disposable_income_ratio', 'credit_utilization_proxy',
            'risk_multiplier', 'age_risk_factor', 'debt_pressure', 'log_income',
            'income_to_loan_ratio', 'debt_service_ratio', 'score_income_index',
            'score_lti_interaction', 'income_tenure_factor'
        ]
        categorical_features = ['employment_type', 'loan_type']
        
        # Preprocessor with Scaling 
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ]
        )
        
        # 3. High-Performance Model
        print("Configuring XGBoost classifier...")
        
        clf_model = XGBClassifier(
            n_estimators=1200,
            learning_rate=0.01,
            max_depth=9,
            subsample=0.85,
            colsample_bytree=0.85,
            gamma=0.1,
            min_child_weight=1,
            reg_alpha=0.1,
            reg_lambda=1.5,
            random_state=42,
            eval_metric='auc'
        )
        
        # 4. Final Balanced Pipeline
        # Calibration helps probability but we keep model complexity for accuracy
        calibrated_model = CalibratedClassifierCV(clf_model, method='sigmoid', cv=5)
        
        clf = ImbPipeline(steps=[
            ('preprocessor', preprocessor),
            ('smote', SMOTETomek(random_state=42)),
            ('classifier', calibrated_model)
        ])
        
        # 5. Training
        X = df.drop(columns=['name', 'default_status'])
        y = df['default_status']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)
        
        print("Fitting model to training data...")
        clf.fit(X_train, y_train)
        
        # 6. Metrics & Deployment
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1]
        
        model_version = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metrics = {
            'accuracy': round(accuracy_score(y_test, y_pred), 4),
            'precision': round(precision_score(y_test, y_pred), 4),
            'recall': round(recall_score(y_test, y_pred), 4),
            'roc_auc': round(roc_auc_score(y_test, y_proba), 4),
            'f1_score': round(f1_score(y_test, y_pred), 4),
            'version': model_version,
            'timestamp': datetime.now().isoformat(),
            'model_type': 'XGBoost Calibrated Classifier'
        }
        
        from ..services.model_registry import ModelRegistry
        
        # Determine model path
        model_filename = f"model_{model_version}.pkl"
        model_storage_dir = os.path.join(base_dir, 'models')
        if not os.path.exists(model_storage_dir):
            os.makedirs(model_storage_dir)
            
        full_model_path = os.path.join(model_storage_dir, model_filename)

        # Persistence
        with open(full_model_path, 'wb') as f:
            pickle.dump(clf, f)
            
        # Also maintain 'risk_model.pkl' as a convenient copy for legacy compat
        with open(os.path.join(base_dir, 'risk_model.pkl'), 'wb') as f:
            pickle.dump(clf, f)
            
        with open(os.path.join(base_dir, 'model_metrics.json'), 'w') as f:
            json.dump(metrics, f)
            
        # Feature names for SHAP (extracting from pipeline)
        ohe = clf.named_steps['preprocessor'].named_transformers_['cat']
        cat_feature_names = ohe.get_feature_names_out(categorical_features).tolist()
        all_features = numeric_features + cat_feature_names
        with open(os.path.join(base_dir, 'feature_columns.json'), 'w') as f:
            json.dump(all_features, f)
            
        # Register in DB Registry
        registry_success = ModelRegistry.register_model(
            version=model_version,
            path=full_model_path,
            metrics=metrics,
            metadata={'model_type': 'Enhanced XGBoost Enterprise', 'features': all_features}
        )
            
        print(f"Model {model_version} trained and deployed: {metrics['accuracy']*100:.2f}% Accuracy")
        return {'success': True, 'metrics': metrics, 'registry': registry_success}
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': str(e)}

if __name__ == "__main__":
    train()
