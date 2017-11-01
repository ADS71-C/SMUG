import pkg_resources
from pymongo import MongoClient, HASHED
import os
from dotenv import load_dotenv


class MongoDBInitializer:
    def __init__(self):
        env_location = pkg_resources.resource_filename('resources', '.env')
        load_dotenv(env_location)

        mongouri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/smug")
        mongodb = os.environ.get("MONGODB_DATABASE", "smug")
        mongocollection = os.environ.get("MONGODB_COLLECTION", "smug")
        client = MongoClient(mongouri)
        db = client[mongodb]
        self.collection = db[mongocollection]

        # self.collection = db[collection]
        self.create_indexes('metadata.url')

    def create_indexes(self, index):
        self.collection.create_index([(index, 1)], unique=True)
