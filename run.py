from backend.app import app

if __name__ == '__main__':
    # Initializing server using settings from Config
    app.run(
        host='0.0.0.0', 
        debug=app.config.get('DEBUG', True), 
        port=app.config.get('PORT', 5000)
    )
