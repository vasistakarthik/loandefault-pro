import sqlite3
import os
import json
from datetime import datetime
from ..database.db import get_db_connection

class ModelRegistry:
    @staticmethod
    def register_model(version, path, metrics, metadata=None):
        """Register a new model in the system."""
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO model_registry 
                (version, path, accuracy, precision_score, recall_score, f1_score, roc_auc, is_active, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                version, path, 
                metrics.get('accuracy'), 
                metrics.get('precision'), 
                metrics.get('recall'), 
                metrics.get('f1_score'), 
                metrics.get('roc_auc'),
                0, # Not active by default
                json.dumps(metadata) if metadata else None
            ))
            
            # If this is the first model, make it active
            count = conn.execute('SELECT COUNT(*) FROM model_registry').fetchone()[0]
            if count == 1:
                conn.execute('UPDATE model_registry SET is_active = 1 WHERE version = ?', (version,))
                
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Model version {version} already exists.")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_active_model():
        """Retrieve the path and metadata of the currently active model."""
        conn = get_db_connection()
        model = conn.execute('SELECT * FROM model_registry WHERE is_active = 1').fetchone()
        conn.close()
        return dict(model) if model else None

    @staticmethod
    def set_active_model(version):
        """Switch the system to a new model version."""
        conn = get_db_connection()
        # Deactivate all
        conn.execute('UPDATE model_registry SET is_active = 0')
        # Activate target
        conn.execute('UPDATE model_registry SET is_active = 1 WHERE version = ?', (version,))
        conn.commit()
        conn.close()

    @staticmethod
    def list_models():
        """List all registered models with their performance metrics."""
        conn = get_db_connection()
        models = conn.execute('SELECT * FROM model_registry ORDER BY trained_at DESC').fetchall()
        conn.close()
        return [dict(m) for m in models]
