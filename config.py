import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'dev'
    # db 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Cache
cache = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 30,
    'CACHE_REDIS_HOST':  'localhost',
    'CACHE_REDIS_PORT': '6379'
}

# Celery
celery_config = {
    'broker_url': "redis://127.0.0.1:6379/0",
    'result_backend': "redis://127.0.0.1:6379/0",
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
}

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'cache': cache,
    'celery': celery_config
}