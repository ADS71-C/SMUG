import simplejson as json

from smug.callback_helper import CallbackForward
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


@CallbackForward('cleaning')
def callback(ch, method, properties, body):
    message = json.loads(body)
    return format_message(message)


if __name__ == '__main__':
    connection_manager = ConnectionManager()
    connection_manager.subscribe('formatting', callback)
