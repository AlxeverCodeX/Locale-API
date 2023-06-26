from pymongo import MongoClient
from ..config.config import Config



def connect_to_db():
    client = MongoClient(Config.connection_string)
    return client.locale