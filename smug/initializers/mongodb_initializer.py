from smug.mongo_manager import MongoManager


class MongoDBInitializer:
    def __init__(self):
        self.mongo_manager = MongoManager()
        self.create_indexes('metadata.url', self.mongo_manager.message_collection, unique=True)
        self.create_indexes('analytics.sickness_score', self.mongo_manager.message_collection)
        self.create_indexes('metadata.date', self.mongo_manager.message_collection)
        self.create_indexes('name', self.mongo_manager.report_collection, unique=True)
        default_reports = [{'name': 'Word vectoring', 'enabled': True, 'parameters': [
            'ziek',
            'griep',
            'verkouden',
            'verkoudheid',
            'koorts',
            'hoofdpijn',
        ]}, {'name': 'Location Prediction', 'enabled': True, 'parameters': []}]
        for report in default_reports:
            self.create_report(report)

    def create_indexes(self, index, collection, unique=False):
        collection.create_index([(index, 1)], unique=unique)

    def create_report(self, report):
        self.mongo_manager.report_collection.update_one({'name': report['name']}, {'$set': report}, upsert=True)
