import os
import pkg_resources
from dotenv import load_dotenv
from pymongo import MongoClient


class MongoManager:
    def __init__(self):
        env_location = pkg_resources.resource_filename('resources', '.env')
        if os.environ.get('DOTENV_LOADED', '0') != '1':
            load_dotenv(env_location)

        mongourl = os.environ.get("MONGO_URI", "mongodb://localhost:27017/smug")
        self.database = os.environ.get("MONGO_DATABASE", "smug")
        self._message_collection_name = os.environ.get("MONGO_MESSAGES_DATABASE", "smug_messages")
        self._report_collection_name = os.environ.get("MONGO_REPORT_DATABASE", "smug_reports")

        client = MongoClient(mongourl, 27017, connect=False)
        self.db = client[self.database]
        self.message_collection = self.db[self._message_collection_name]
        self.report_collection = self.db[self._report_collection_name]

    def get_reports(self):
        reports = self.report_collection.find({"enabled": True})

        return reports
