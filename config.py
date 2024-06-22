import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'dev'

    # db config
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # mail config
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEBUG = False
    MAIL_DEFAULT_SENDER = 'adminlms@email.com'

    # celery config
    broker_url = "redis://127.0.0.1:6379/0"
    result_backend = "redis://127.0.0.1:6379/0"
    task_serializer = 'json'
    broker_connection_retry_on_startup = True
    result_serializer = 'json'
    accept_content = ['json']

    # redis cache config
    CACHE_TYPE = 'RedisCache'
    CACHE_DEFAULT_TIMEOUT = 30
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = '6379'


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}