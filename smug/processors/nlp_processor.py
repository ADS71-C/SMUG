import pkg_resources
import json
from bson import json_util

from mongo_manager import MongoManager
from smug.callback_helper import CallbackForward
from smug.connection_manager import ConnectionManager


class NlpProcessor:
    def __init__(self):
        self.mongo_manager = MongoManager()
        self.reports = [result for result in self.mongo_manager.get_reports() if result['type'] == 'nlp']

    def score(self, message):
        message['reports'] = []
        for report in self.reports:
            message['reports'].append({
                'id': str(report['_id']),
            })
        return message


@CallbackForward("save")
def callback(ch, method, properties, body):
    message = json.loads(body, object_hook=json_util.object_hook)
    return word_vector_processor.score(message)


if __name__ == '__main__':
    word_vector_processor = NlpProcessor()
    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_queue('process_nlp', callback)
