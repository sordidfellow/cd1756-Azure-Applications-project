#!/usr/bin/env python3
"""
Local development script for FlaskWebProject with debugging enabled and file logging.
"""

import os
import json
import logging
from logging.handlers import RotatingFileHandler

# Set local development mode BEFORE importing app
os.environ['LOCAL_DEV'] = 'true'

# Set up SQLite for local development
os.environ['LOCAL_DB'] = os.path.join(os.path.dirname(__file__), 'local_dev.db')

from FlaskWebProject import app

# Load environment variables from webapp_secrets.json
settings_file = os.path.join(os.path.dirname(__file__), 'webapp_secrets.json')
if os.path.exists(settings_file):
    with open(settings_file, 'r') as f:
        settings = json.load(f)
        for setting in settings:
            os.environ[setting['name']] = setting['value']
            # print(f"{setting['name']} = {setting['value']}")
    print("Loaded environment variables from webapp_secrets.json")

# Set local development mode
os.environ['LOCAL_DEV'] = 'true'

# Enable debug mode
app.debug = True

# Set up file logging
log_file = os.path.join(os.path.dirname(__file__), 'app.log')
file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add file handler to app logger
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)

# Also log werkzeug (Flask's underlying server)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addHandler(file_handler)
werkzeug_logger.setLevel(logging.DEBUG)

# Create database tables for local development
if os.environ.get('LOCAL_DEV') == 'true':
    from FlaskWebProject import db
    from FlaskWebProject.models import User
    with app.app_context():
        db.create_all()
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('pass')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created (username: admin, password: pass)")
        print("Database tables created for local development.")
        # Ensure local image directory exists
        local_image_dir = os.path.join(os.path.dirname(__file__), 'FlaskWebProject', 'static', 'images')
        os.makedirs(local_image_dir, exist_ok=True)

if __name__ == '__main__':
    print(f"Starting Flask app in debug mode...")
    print(f"Logs will be written to: {log_file}")
    print("Access the app at: http://localhost:5555")
    print("Press Ctrl+C to stop")

    # Run without SSL for local development
    app.run(host='localhost', port=5555, debug=True)