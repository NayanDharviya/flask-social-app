
# base class
class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = "3f4twrgfhndi34"
    
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'root'
# app.config['MYSQL_DB'] = 'user'

    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "root"
    MYSQL_DB = "user"

    UPLOADS = "/home/username/app/app/static/images/uploads"

# cookies are protected with https secured
    SESSION_COOKIES_SECURE = True


# child class
class ProductionConfig(Config):
    # ENV = "production"
    pass

# child class inherit Config
class DevelopmentConfig(Config):
    DEBUG = True

    DB_NAME = "user"
    DB_USERNAME = "root"
    DB_PASSWORD = "root"

    
    UPLOADS = "/home/username/projects/flask_app/app/app/static/images/uploads"

    SESSION_COOKIES_SECURE = False


class TestingConfig(Config):
    TESTING = True
    
    UPLOADS = "/home/username/app/app/static/images/uploads"

    SESSION_COOKIES_SECURE = False