# CONFIGURATION FILE FOR FLASK APP
# Contains configuation class for the Flask app, including database connection, session configuration, and secret key.

from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os

# create db and session objects
if 'db' not in globals():
    db = SQLAlchemy()
session = Session()


# configuration class for the Flask app
class Config:

    # secret key for session
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # session configuration
    SESSION_TYPE = 'sqlalchemy'
    SESSION_PERMANENT = False
    SESSION_SQLALCHEMY = db

    # db connection configuration (conditionally set based on environment)
    DATABASE_URL_DEV = os.environ.get('DATABASE_URL_DEV')
    DATABASE_URL_PROD = os.environ.get('DATABASE_URL_PROD')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL_DEV if os.environ.get('RUN_DEV') == "True" else DATABASE_URL_PROD
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF protection
    WTF_CSRF_ENABLED = True