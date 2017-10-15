import simplejson as json

from smug.callback_helper import CallbackHelper
from smug.connection_manager import ConnectionManager


def format_message(original_message):
    formatted_message = {
        'message': original_message['bericht tekst'],
        'author': original_message['auteur'],
        'metadata': {
            'date': original_message['datum'],
            'url': original_message['url'],
            'type': original_message['type'],
        }
    }

    return formatted_message


def callback(ch, method, properties, body):
    message = json.loads(body)
    return format_message(message)


if __name__ == '__main__':
    connection_manager = ConnectionManager()
    callback_helper = CallbackHelper(callback=callback, forward_channel_type='cleaning')
    connection_manager.subscribe('formatting', callback_helper.wrapped_callback)
