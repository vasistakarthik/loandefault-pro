---
description: Enterprise deployment and MLOps maintenance for LoanRisk Pro
---

# Enterprise Deployment Workflow

Follow these steps to deploy and maintain the Enterprise AI Credit Risk platform.

## 1. Environment Setup
- Copy `.env.example` to `.env`
- Configure `SECRET_KEY` and `DATABASE_URL`
- Ensure `MODEL_STORAGE_PATH` exists

## 2. Secure Initialization
// turbo
- `python init_database.py` (Applies all schema migrations and indexes)
- `python add_advanced_indexes.py` (Adds performance optimizations)

## 3. Initial Model Training
// turbo
- `python -m backend.model.train_model` (Trains the initial XGBoost model and registers version v1.0)

## 4. Local Deployment (Testing)
// turbo
- `gunicorn --bind 0.0.0.0:8000 backend.app:app`

## 5. Containerized Cloud Deployment
- `docker build -t loanrisk-enterprise .`
- `docker run -p 8000:8000 --env-file .env loanrisk-enterprise`

## 6. MLOps Maintenance
- Access `/admin/model-metrics` to monitor drift
- Use the **Retrain** button to trigger automated updates
- Historical risk data is automatically logged to `audit_logs` for governance review
