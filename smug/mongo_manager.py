import os
import pkg_resources
from dotenv import load_dotenv
from pymongo import MongoClient

class MongoConfig:
    """
    MongoDB configuration object. This object can be used to create a custom configuration for the MongoDB connection.

    Examples:
        >>> from smug.mongo_manager import MongoConfig, MongoManager
        >>> mongo_config = MongoConfig(port=12345)
    This will create a config with all of the default values from the environment file
    with the exception of the ``port`` which will be `12345`. This config can then be used with the ``MongoManager`` in
    order to use this custom config.
        >>> mongo_manager = MongoManager(config=mongo_config)

    Args:
        mongo_url (str, optional): The url of the collection to connect to. If no value is provided value will be read from
            `MONGO_URI` variable in the environment file.
        database (str, optional): Name of the database to connect to. If no value is provided value will be read from
            `MONGO_DATABASE` variable in the environment file.
        port (int, optional): The port to connect to. If 'no value is provided the port will be the default port for 
            mongo db this is port `27017` 
        message_collection_name (str, optional): Name of the collection storing the message. If no value is provided value
            will be read from `MONGO_MESSAGES_DATABASE` variable in the environment file.
        report_collection_name (str, optional): Name of the collection storing the reports. If no value is provided value
            will be read from `MONGO_REPORT_DATABASE` variable in the environment file.

    Note:
        If no parameters are passed the default values from the environment file will be used.
    """
    def __init__(self, mongo_url: str = '', database: str = '', port:int = -1, message_collection_name: str = '',
                 report_collection_name: str = ''):
        env_location = pkg_resources.resource_filename('resources', '.env')
        load_dotenv(env_location)

        self.mongo_url = mongo_url if mongo_url != '' else os.environ.get("MONGO_URI", "mongodb://localhost:27017/smug")
        self.database = database if database != '' else os.environ.get("MONGO_DATABASE", "smug")
        self.port = port if port != -1 else 27017
        self.message_collection_name = message_collection_name if message_collection_name != '' \
            else os.environ.get("MONGO_MESSAGES_DATABASE", "smug_messages")
        self.report_collection_name = report_collection_name if report_collection_name != '' \
            else os.environ.get("MONGO_REPORT_DATABASE", "smug_reports")


class MongoManager:
    """
    Class for connecting to MongoDB server. This class ensures that all MongoDB connections have the correct properties
    and configs. This class should be used when connecting to a MongoDB database.

    Examples:
        >>> from smug.mongo_manager import MongoManager
        >>> mongo_manager = MongoManager()
    Now that we have our ``MongoManager`` we can use it's message_collection attribute in order to interact with our
    `message collection`.
        >>> mongo_manager.message_collection.insert('test')

    Args:
        config (MongoConfig, optional): The configuration used by the manager. For available options see ``MongoConfig``

    """
    def __init__(self, config: MongoConfig = MongoConfig()):
        client = MongoClient(config.mongo_url, config.port, connect=False)
        self.db = client[config.database]
        self.message_collection = self.db[config.message_collection_name]
        self.report_collection = self.db[config.report_collection_name]

    def get_reports(self):
        """
        Retrieves active reports from the ``report_collection``

        Returns:
            pymongo.cursor.Cursor: Cursor containing all the enabled reports in the reports_collection.

        """
        reports = self.report_collection.find({"enabled": True})

        return reports
