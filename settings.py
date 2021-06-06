class Config(object):
    FLASK_ENV = 'development'
    TESTING = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://db_user:db_password@db-postgres:5432/code'
    BROKER = 'pyamqp://rabbit_user:rabbit_password@broker-rabbitmq//'
