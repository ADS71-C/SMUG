import simplejson as json
from bson import json_util

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
            'source': 'twitter',
            'source_import': 'coosto'
        }
    }

    return formatted_message


@CallbackForward('clean')
def callback(ch, method, properties, body):
    message = json.loads(body, object_hook=json_util.object_hook)
    return format_message(message)


if __name__ == '__main__':
    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_routing_key('formatter.coosto', callback)
