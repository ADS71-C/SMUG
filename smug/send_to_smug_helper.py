import hashlib
from functools import wraps

import os
import json
import pkg_resources
import re

from bson import json_util
from dotenv import load_dotenv

from connection_manager import ConnectionManager


class SendToSmugHelper:
    """
    A wrapper class that takes care of sending any sort of data to smug
    """
    def __init__(self):
        self.connection_manager = ConnectionManager()
        env_location = pkg_resources.resource_filename('resources', '.env')
        if os.environ.get('DOTENV_LOADED', '0') != '1':
            load_dotenv(env_location)
        self.personal = os.environ.get("BLAKE2D_KEY", "topsecretkey").encode()

    def __call__(self, func):
        outer_self = self

        @wraps(func)
        def wrapper(*args, **kwds):
            message = func(*args, **kwds)
            message['reports'] = []

            if message is not None and 'nl' in message['metadata']['lang']:
                author_hash = outer_self._hash(message['author'])
                message_with_hashes = re.sub(r'@(\w+)', outer_self.hash_username, message['message'])

                message['author'] = author_hash
                message['message'] = message_with_hashes

                outer_self.connection_manager.publish_to_queue('clean',
                                                         json.dumps(message, default=json_util.default))
        return wrapper

    def hash_username(self, username):
        return '@{}'.format(self._hash(username.group(1)))

    def _hash(self, text):
        h = hashlib.blake2b(digest_size=12, person=self.personal)
        h.update(text.encode('utf-8'))
        return h.hexdigest()
