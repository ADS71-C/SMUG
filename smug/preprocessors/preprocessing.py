import re
import simplejson as json
from bson import json_util

from smug.callback_helper import CallbackForward
from smug.connection_manager import ConnectionManager


def split_words(message):
    message['message'] = message['message'].lower()
    text = re_clean.sub(' ', message['message'])
    message['metadata']['message_words'] = re_words.findall(text)
    return message


@CallbackForward('process')
def callback(ch, method, properties, body):
    message = json.loads(body, object_hook=json_util.object_hook)
    return split_words(message)


if __name__ == '__main__':
    re_clean = re.compile(r'(https?://\S+|@\S+)')
    re_words = re.compile(r'(\w+-?\w*)')

    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_queue('preprocess', callback)
