from flask import Blueprint, render_template, session, redirect, url_for, send_file, request
from ..database.db import get_db_connection
import pandas as pd
from io import BytesIO
from datetime import datetime
import os
import json

report_bp = Blueprint('report', __name__)

@report_bp.before_request
def require_login():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@report_bp.route('/reports')
def view_reports():
    conn = get_db_connection()
    
    # 1. Total Institutional Exposure (Archive + Live)
    history_exposure = conn.execute("SELECT SUM(loan_amount) FROM loan_history").fetchone()[0] or 0.0
    live_exposure = conn.execute("SELECT SUM(loan_amount) FROM loan_applications").fetchone()[0] or 0.0
    total_exposure = history_exposure + live_exposure
    
    # 2. Node Counts
    history_count = conn.execute("SELECT COUNT(*) FROM loan_history").fetchone()[0] or 0
    live_count = conn.execute("SELECT COUNT(*) FROM loan_applications").fetchone()[0] or 0
    total_nodes = history_count + live_count

    # 3. Portfolio Integrity (Non-Defaulted %)
    defaults = conn.execute("SELECT COUNT(*) FROM loan_history WHERE status = 'Defaulted'").fetchone()[0] or 0
    live_defaults = conn.execute("SELECT COUNT(*) FROM loan_applications WHERE status = 'Defaulted'").fetchone()[0] or 0
    total_defaults = defaults + live_defaults
    
    integrity_index = 100 * (1 - (total_defaults / (total_nodes if total_nodes > 0 else 1)))
    
    # 4. Exposure at Risk (Sum of defaulted/high risk principals)
    exposure_at_risk = conn.execute("SELECT SUM(loan_amount) FROM loan_history WHERE status = 'Defaulted'").fetchone()[0] or 0.0
    live_ear = conn.execute("SELECT SUM(loan_amount) FROM loan_applications WHERE risk_band = 'High Risk'").fetchone()[0] or 0.0
    total_ear = exposure_at_risk + live_ear

    # 5. Network Metrics
    avg_stats = conn.execute('''
        SELECT AVG(credit_score) as avg_score, AVG(annual_income) as avg_income 
        FROM (SELECT credit_score, annual_income FROM borrowers)
    ''').fetchone()

    # 6. Scatter Data: Neural Risk Distribution (Income vs Principal)
    scatter_query = conn.execute('''
        SELECT annual_income as x, loan_amount as y FROM loan_history
        UNION ALL
        SELECT b.annual_income as x, la.loan_amount as y 
        FROM loan_applications la
        JOIN borrowers b ON la.borrower_id = b.id
        LIMIT 500
    ''').fetchall()
    
    # 7. Segmentation Matrix (Low, Med, High)
    h_risk = conn.execute("SELECT COUNT(*) FROM loan_history WHERE status = 'Defaulted'").fetchone()[0] or 0
    h_low = conn.execute("SELECT COUNT(*) FROM loan_history WHERE status = 'Paid'").fetchone()[0] or 0
    h_med = conn.execute("SELECT COUNT(*) FROM loan_history WHERE status = 'Ongoing'").fetchone()[0] or 0
    
    l_high = conn.execute("SELECT COUNT(*) FROM loan_applications WHERE risk_band = 'High Risk'").fetchone()[0] or 0
    l_med = conn.execute("SELECT COUNT(*) FROM loan_applications WHERE risk_band = 'Medium Risk'").fetchone()[0] or 0
    l_low = conn.execute("SELECT COUNT(*) FROM loan_applications WHERE risk_band = 'Low Risk'").fetchone()[0] or 0
    
    segmentation = {
        'low': h_low + l_low,
        'medium': h_med + l_med,
        'high': h_risk + l_high
    }

    import json
    data_pack = {
        'scatter': [dict(r) for r in scatter_query],
        'pie': [segmentation['low'], segmentation['medium'], segmentation['high']]
    }
    
    conn.close()
    
    return render_template('reports.html', 
                          total_nodes=total_nodes,
                          total_exposure=total_exposure,
                          total_ear=total_ear,
                          total_defaults=total_defaults,
                          integrity_index=round(integrity_index, 1),
                          avg_score=int(avg_stats['avg_score'] or 650),
                          avg_income=int(avg_stats['avg_income'] or 850000),
                          data_pack=json.dumps(data_pack))

@report_bp.route('/analytics')
def analytics():
    conn = get_db_connection()
    
    risk_counts = conn.execute('''
        SELECT 
            SUM(CASE WHEN risk_band = 'Low Risk' THEN 1 ELSE 0 END) as low,
            SUM(CASE WHEN risk_band = 'Medium Risk' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN risk_band = 'High Risk' THEN 1 ELSE 0 END) as high
        FROM loan_applications
    ''').fetchone()
    
    scatter_query = conn.execute('''
        SELECT b.annual_income as income, la.loan_amount 
        FROM loan_applications la
        JOIN borrowers b ON la.borrower_id = b.id
    ''').fetchall()
    
    import json
    scatter_data = [{'x': row['income'], 'y': row['loan_amount']} for row in scatter_query]
    scatter_data_json = json.dumps(scatter_data)
    
    conn.close()
    
    return render_template('analytics.html', 
                          risk_stats={'low': (risk_counts['low'] or 0), 'medium': (risk_counts['medium'] or 0), 'high': (risk_counts['high'] or 0)}, 
                          scatter_data=scatter_data_json)

@report_bp.route('/export/<fmt>')
def export_data(fmt):
    """Secure Data Export: CSV or Excel."""
    conn = get_db_connection()
    query = '''
        SELECT 
            la.id, b.full_name as applicant, b.annual_income, 
            la.loan_amount, la.risk_band, la.status, la.created_at
        FROM loan_applications la
        JOIN borrowers b ON la.borrower_id = b.id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if fmt == 'csv':
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f"Loan_Export_{timestamp}.csv")
    
    elif fmt == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Applications')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f"Loan_Export_{timestamp}.xlsx")
    
    return "Invalid Format", 400

@report_bp.route('/model_performance')
def model_performance():
    """MLOps Performance Terminal - displays real-time model accuracy metrics."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    metrics_path = os.path.normpath(os.path.join(base_dir, '..', 'model', 'model_metrics.json'))
    
    metrics = {
        "accuracy": 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "roc_auc": 0.0,
        "f1_score": 0.0,
        "version": "v1.0.0-fallback",
        "timestamp": datetime.now().isoformat(),
        "model_type": "None"
    }
    
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                content = f.read()
                if content:
                    metrics = json.loads(content)
        except Exception as e:
            print(f"Error loading metrics: {e}")

    return render_template('model_performance.html', metrics=metrics)
