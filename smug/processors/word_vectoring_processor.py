from gensim.models.word2vec import Word2Vec
import pkg_resources
import json

from smug.callback_helper import CallbackHelper
from smug.connection_manager import ConnectionManager


def score(message):
    words = [word for word in message['metadata']['message_words'] if word in model.wv.vocab]
    score = 0
    if words:
        score = model.wv.n_similarity(sickness_terms, words)
    if message['metadata']['type'] == 'comment':
        score /= 2
    message['analytics'] = {
        'sickness_score': score,
        'scored_words': words
    }
    return message


def callback(ch, method, properties, body):
    message = json.loads(body)
    return score(message)


if __name__ == '__main__':
    sickness_terms = [
        'ziek',
        'griep',
        'verkouden',
        'verkoudheid',
        'koorts',
        'hoofdpijn',
    ]

    model_location = pkg_resources.resource_filename('resources', 'word2vec.model')
    model = Word2Vec.load(model_location)
    connection_manager = ConnectionManager()
    callback_helper = CallbackHelper(callback=callback, forward_channel_type='save')
    connection_manager.subscribe('processing', callback_helper.wrapped_callback)
