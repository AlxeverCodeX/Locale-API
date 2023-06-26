import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
from datetime import timedelta


load_dotenv(find_dotenv())

class Config:
    secret_key = os.environ.get('SECRET_KEY')
    connection_string = os.environ.get('MONGO')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

class DevConfig(Config):
    DEBUG = os.environ.get('FLASK_DEBUG')

class TestConfig(Config):
    pass
    
class ProdConfig(Config):
    pass

config_dict = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig
}

