import os


DB_USER = os.environ['POSTGRES_USER']
DB_PASS = os.environ['POSTGRES_PASSWORD']
DB_HOST = os.environ['POSTGRES_HOST']
DB_PORT = os.environ['POSTGRES_PORT']
DB_NAME = os.environ['POSTGRES_DB']


class Config(object):
    FLASK_ENV = 'development'
    TESTING = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = 'redis://redis:6379/0'
