import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'frey.maxim@gmail.com'
    MAIL_PASSWORD = 'Airjeff3'
    FLASKY_MAIL_SUBJECT_PREFIX = '[JeffPD]'
    FLASKY_MAIL_SENDER = 'frey.maxim@gmail.com'
    FLASKY_ADMIN = 'frey.maxim@gmail.com'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres://uaaalnaflmsjnp:pLyQ5JRVbro0WCgXuMVorfqSjY@ec2-54-227-255-240.compute-1.amazonaws.com:5432/d8hosmtv1eijgp'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgres://uaaalnaflmsjnp:pLyQ5JRVbro0WCgXuMVorfqSjY@ec2-54-227-255-240.compute-1.amazonaws.com:5432/d8hosmtv1eijgp'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgres://uaaalnaflmsjnp:pLyQ5JRVbro0WCgXuMVorfqSjY@ec2-54-227-255-240.compute-1.amazonaws.com:5432/d8hosmtv1eijgp'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
