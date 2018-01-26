
class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '728f098ccb86a7dd52e4655028af3e0dd4da2b8d67e56f76'                 # Don't share it
    SQLALCHEMY_DATABASE_URI = 'postgresql://flask_admin:root@localhost/flaskapp'    # Database address
    SQLALCHEMY_TRACK_MODIFICATIONS = False                                          # Track model modifications

class ProdConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestConfig(Config):
    TESTING = True