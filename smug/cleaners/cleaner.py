import simplejson as json

from smug.callback_helper import CallbackHelper
from smug.connection_manager import ConnectionManager


def clean(message):
    if message['message'] is None:
        message['message'] = ''
    if 'rt' in message['message']:
        return None
    if 'http' in message['message']:
        return None
    return message


def callback(ch, method, properties, body):
    message = json.loads(body)
    return clean(message)


if __name__ == '__main__':
    connection_manager = ConnectionManager()
    callback_helper = CallbackHelper(callback=callback, forward_channel_type='preprocessing')
    connection_manager.subscribe('cleaning', callback_helper.wrapped_callback)
    print('Cleaner started')
