@echo off
echo ===================================================
echo   Starting Loan Default Prediction System
echo ===================================================

echo Installing dependencies...
pip install -r backend/requirements.txt

echo.
echo Starting Application...
python run.py

pause
