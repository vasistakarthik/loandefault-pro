import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost import XGBClassifier
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "data", "loan_dataset.csv")
df = pd.read_csv(data_path)

# Quick Features
usd_rate = 85.0
df['dti'] = (df['existing_emi'] + (df['loan_amount'] / df['tenure'])) / (df['income'] / 12)
df['lti'] = df['loan_amount'] / df['income']

drop_cols = ['name', 'default_status']
X = df.drop(columns=drop_cols)
y = df['default_status']
X = pd.get_dummies(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

param_grid = {
    'max_depth': [6, 10, 15],
    'learning_rate': [0.01, 0.1, 0.2],
    'n_estimators': [100, 300, 500],
    'subsample': [0.8, 1.0]
}

grid = GridSearchCV(XGBClassifier(use_label_encoder=False, eval_metric='logloss'), param_grid, cv=3, scoring='accuracy', verbose=1)
grid.fit(X_train, y_train)

print(f"Best Score: {grid.best_score_}")
print(f"Best Params: {grid.best_params_}")
