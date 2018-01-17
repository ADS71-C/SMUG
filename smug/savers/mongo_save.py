import pkg_resources
from pymongo import UpdateOne
import os
from dotenv import load_dotenv
import simplejson as json
from bson import json_util
import threading

from smug.mongo_manager import MongoManager
from smug.connection_manager import ConnectionManager


class MongoSave():
    def __init__(self, write_buffer_size, buffer_enabled=True):
        self.buffer = {}
        self.write_buffer_size = write_buffer_size
        self.ch = None
        self.mongo_manager = MongoManager()
        self.lock = threading.RLock()
        self.buffer_enabled = buffer_enabled

    def save(self):
        self.lock.acquire()
        if len(self.buffer) > 0:
            messages = self.buffer.values()
            latest_message = json.dumps(list(messages)[-1], default=json_util.default)
            connection_manager.publish_to_queue('latest', latest_message)
            requests = [UpdateOne({'metadata.url': value['metadata']['url']},
                                  {'$setOnInsert': {
                                      'metadata': value['metadata'],
                                      'author': value['author'],
                                      'message': value['message']
                                  },
                                      '$addToSet': {'reports': {"$each": value['reports']}}},
                                  upsert=True)
                        for value in messages]
            for delivery_tag in self.buffer:
                # Ack to the MQ
                self.ch.basic_ack(delivery_tag=delivery_tag)

            self.mongo_manager.message_collection.bulk_write(requests)
            self.buffer.clear()
        self.lock.release()

    def callback(self, ch, method, properties, body):
        self.lock.acquire()
        self.ch = ch
        self.buffer[method.delivery_tag] = (json.loads(body, object_hook=json_util.object_hook))
        self.lock.release()

        # Writes to the database if the buffer is the correct length
        if len(self.buffer) >= self.write_buffer_size or not self.buffer_enabled:
            self.save()


if __name__ == '__main__':
    env_location = pkg_resources.resource_filename('resources', '.env')
    if os.environ.get('DOTENV_LOADED', '0') != '1':
        load_dotenv(env_location)
    mongouri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/smug")
    mongodb = os.environ.get("MONGODB_DATABASE", "smug")
    write_buffer_size = int(os.environ.get("MONGO_WRITE_BUFFER", 100))
    prefetch_count = int(os.environ.get("PREFETCH_COUNT", 500))

    if write_buffer_size > prefetch_count:
        raise ValueError('MongoDB write buffer should not exceed prefetch count. This will cause the')

    mongo_save = MongoSave(write_buffer_size=write_buffer_size, buffer_enabled=True)
    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_queue('save', mongo_save.callback)
