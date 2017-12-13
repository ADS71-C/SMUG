import pkg_resources
import json
from bson import json_util

from smug.mongo_manager import MongoManager
from smug.callback_helper import CallbackForward
from smug.connection_manager import ConnectionManager

from textblob import TextBlob


class NlpProcessor:
    def __init__(self):
        self.mongo_manager = MongoManager()
        self.reports = [result for result in self.mongo_manager.get_reports() if result['type'] == 'nlp']

    def score(self, message):
        message['reports'] = []
        tb = TextBlob(message['message'])
        for report in self.reports:
            result = {}
            if report['mode'] == 'sentiment':
                sentiment = tb.translate(to='en').sentiment  # sentiment analysis only works in english
                result['polarity'] = sentiment.polarity
                result['subjectivity'] = sentiment.subjectivity

            message['reports'].append({
                'id': str(report['_id']),
                **report
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
