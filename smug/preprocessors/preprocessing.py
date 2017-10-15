import re
import simplejson as json

from smug.callback_helper import CallbackHelper
from smug.connection_manager import ConnectionManager


def split_words(message):
    message['message'] = message['message'].lower()
    text = re_clean.sub(' ', message['message'])
    message['metadata']['message_words'] = re_words.findall(text)
    return message


def callback(ch, method, properties, body):
    message = json.loads(body)
    return split_words(message)


if __name__ == '__main__':
    re_clean = re.compile(r'(https?://\S+|@\S+)')
    re_words = re.compile(r'(\w+-?\w*)')

    connection_manager = ConnectionManager()
    callback_helper = CallbackHelper(callback=callback, forward_channel_type='processing')
    connection_manager.subscribe('preprocessing', callback_helper.wrapped_callback)
