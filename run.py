from backend.app import app

if __name__ == '__main__':
    # The database initialization is handled inside backend/app.py 
    # under the 'with app.app_context():' block.
    app.run(host='0.0.0.0', debug=True, port=5000)
