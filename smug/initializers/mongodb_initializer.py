import pkg_resources
from pymongo import MongoClient
from pymongo import TEXT
import os
from dotenv import load_dotenv


class MongoDBInitializer:
    def __init__(self):
        env_location = pkg_resources.resource_filename('resources', '.env')
        load_dotenv(env_location)

        mongourl = os.environ.get("MONGO_URL", "localhost")
        database = os.environ.get("MONGO_DATABASE", "smug")
        collection = os.environ.get("MONGO_COLLECTION", "smug")

        client = MongoClient(mongourl, 27017)
        db = client[database]

        self.collection = db[collection]
        self.create_indexes('metadata.url')

    def create_indexes(self, index):
        self.collection.create_index([(index, TEXT)], unique=True)
