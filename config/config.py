# CONFIGURATION FILE FOR FLASK APP
# Contains configuation class for the Flask app, including database connection, session configuration, and secret key.

from dotenv import load_dotenv
import os

# load environment variables
load_dotenv(override=True)

class Config:
    """Base configuration."""
    # secret key for session
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # session configuration
    SESSION_TYPE = 'sqlalchemy'
    SESSION_PERMANENT = False

    # db connection configuration (conditionally set based on environment)
    DATABASE_URL_DEV = os.environ.get('DATABASE_URL_DEV')
    DATABASE_URL_PROD = os.environ.get('DATABASE_URL_PROD')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL_DEV if os.environ.get('RUN_DEV') == "True" else DATABASE_URL_PROD
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF protection
    WTF_CSRF_ENABLED = True

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'
    # Add development-specific configurations here

class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for tests
    LOGIN_DISABLED = True  # Disable login for testing
    SESSION_TYPE = 'sqlalchemy'
    SESSION_PERMANENT = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'