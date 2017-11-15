import simplejson as json

from smug.callback_helper import CallbackForward
from smug.connection_manager import ConnectionManager


def clean(message):
    if message['message'] is None:
        message['message'] = ''

    if 'metadata' not in message:
        return None  # no metadata provided! Should not happen

    if 'rt' in message['message'].lower():
        return None
    if 'http' in message['message']:
        return None
    return message


@CallbackForward('preprocess')
def callback(ch, method, properties, body):
    message = json.loads(body)
    return clean(message)


if __name__ == '__main__':
    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_queue('clean', callback)
    print('Cleaner started')
