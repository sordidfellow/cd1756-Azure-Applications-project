"""
The flask application package.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session


def setup_logging(app):
    """Configure logging to stream and file."""
    if not app.debug:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Create rotating file handler
        file_handler = RotatingFileHandler('logs/app.log', 
                                           maxBytes=10240000,  # 10MB
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    # Console stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    stream_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(stream_handler)
    
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Application startup')


app = Flask(__name__)
app.config.from_object(Config)
setup_logging(app)

Session(app)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

import FlaskWebProject.views
