import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class BaseConfig(object):
    """Base configuration."""

    APP_NAME = os.getenv("APP_NAME")
    DEBUG_TB_ENABLED = False
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    DEBUG = False
    SERVER_NAME = os.environ.get("SERVER_NAME")
    RESULTS_PER_PAGE = 7
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    SHOW_HEADER = os.getenv("SHOW_HEADER", True)
    DSN = os.getenv("DSN")
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_DEV") or 'postgresql://localhost/price-picker-dev'
    DEBUG = True


class TestingConfig(BaseConfig):
    """Testing configuration."""

    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_TEST") or 'postgresql://localhost/price-picker-test'
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    TESTING = False
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


configs = {
    'DEV': DevelopmentConfig,
    'PROD': ProductionConfig,
    'TEST': TestingConfig,
    'DEFAULT': DevelopmentConfig
}
