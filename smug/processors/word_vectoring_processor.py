from gensim.models.word2vec import Word2Vec
import pkg_resources
import json
from bson import json_util

from smug.mongo_manager import MongoManager
from smug.callback_helper import CallbackForward
from smug.connection_manager import ConnectionManager


class WordVectorProcessor:
    def __init__(self):
        self.mongo_manager = MongoManager()
        self.reports = [result for result in self.mongo_manager.get_reports()
                        if result.get('type', 'wordvec') == 'wordvec']
        model_location = pkg_resources.resource_filename('resources', 'model/word2vec.model')
        self.model = Word2Vec.load(model_location)

    def score(self, message):
        words = [word for word in message['metadata']['message_words'] if word in self.model.wv.vocab]
        for report in self.reports:
            score = 0
            if words:
                score = self.model.wv.n_similarity(report['parameters'], words)
                score = ((-1 / (len(words) * 15 + 1)) + 1) * score
            if message['metadata']['type'] == 'comment':
                score /= 2
            message['reports'].append({
                'id': str(report['_id']),
                'score': score,
                'scored_words': words
            })
        return message


@CallbackForward("save")
def callback(ch, method, properties, body):
    message = json.loads(body, object_hook=json_util.object_hook)
    return word_vector_processor.score(message)


if __name__ == '__main__':
    word_vector_processor = WordVectorProcessor()
    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_queue('process_wordvec', callback)
