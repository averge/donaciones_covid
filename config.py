from os import environ
from dotenv import load_dotenv, find_dotenv

ENVIRONMENT = None
UPLOADS_PUBLIC_DIRECTORY = None
if load_dotenv(find_dotenv()):
    ENVIRONMENT = environ.get("FLASK_ENV")
    UPLOADS_PUBLIC_DIRECTORY = environ.get(
        "UPLOADS_PUBLIC_DIRECTORY",
        "./app/static/uploads/"
    )
else:
    raise AssertionError("No se pudo levantar el dotenv")


class BaseConfig(object):
    """Base configuration."""

    DEBUG = None
    DB_HOST = "bd_name"
    DB_USER = "db_user"
    DB_PASS = "db_pass"
    DB_NAME = "db_name"
    SQLALCHEMY_DATABASE_URI = "sql_alchemy_uri"
    SECRET_KEY = "secret"

    @staticmethod
    def configure(app):
        # Implement this method to do further configuration on your app.
        pass


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    ENV = "development"
    DEBUG = environ.get("DEBUG", True)
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")


class TestingConfig(BaseConfig):
    """Testing configuration."""

    ENV = "testing"
    TESTING = True
    DEBUG = environ.get("DEBUG", True)
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")


class ProductionConfig(BaseConfig):
    """Production configuration."""

    ENV = "production"
    DEBUG = environ.get("DEBUG", False),
    SESSION_COOKIE_SECURE = True,
    SESSION_COOKIE_HTTPONLY = True,
    SQLALCHEMY_DATABASE_URI = environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "mysql+pymysql://grupo42:OGU3OGI4NWQ0ZGZl@localhost/grupo42"
    )


config = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)
