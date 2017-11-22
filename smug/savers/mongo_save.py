import pkg_resources
from pymongo import UpdateOne
import os
from dotenv import load_dotenv
import simplejson as json
from bson import json_util
import threading

from mongo_manager import MongoManager
from smug.connection_manager import ConnectionManager


class MongoSave():
    def __init__(self, write_buffer_size):
        self.buffer = {}
        self.write_buffer_size = write_buffer_size
        self.ch = None
        self.mongo_manager = MongoManager()
        self.lock = threading.RLock()

    def save(self):
        self.lock.acquire()
        if len(self.buffer) > 0:
            requests = [UpdateOne({'metadata.url': value['metadata']['url']},
                                  {'$setOnInsert': {
                                      'metadata': value['metadata'],
                                      'author': value['author'],
                                      'message': value['message']
                                  },
                                   '$addToSet': {'reports': {"$each": value['reports']}}},
                                  upsert=True)
                        for value in self.buffer.values()]
            self.mongo_manager.message_collection.bulk_write(requests)

            for delivery_tag in self.buffer:
                # Ack to the MQ
                self.ch.basic_ack(delivery_tag=delivery_tag)
            self.buffer.clear()
        self.lock.release()

    def callback(self, ch, method, properties, body):
        # The watchdog will only start if it has not been started already
        self.lock.acquire()
        watchdog.start()
        self.ch = ch
        self.buffer[method.delivery_tag] = (json.loads(body, object_hook=json_util.object_hook))
        # Refresh the watchdog
        self.lock.release()
        watchdog.refresh()

        # Writes to the database if the buffer is the correct length
        if len(self.buffer) >= self.write_buffer_size:
            self.save()


class MongoSaveWatchdog:
    def __init__(self, callback, threshold=10):
        self.timeout = threshold
        self._t = None
        self.callback = callback

    def _expire(self):
        print("Buffer threshold exceeded writing to database")
        self.callback()

    def start(self):
        if self._t is None:
            self._t = threading.Timer(self.timeout, self._expire)
            self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None

    def refresh(self):
        if self._t is not None:
            self.stop()
            self.start()


if __name__ == '__main__':
    env_location = pkg_resources.resource_filename('resources', '.env')
    load_dotenv(env_location)
    mongouri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/smug")
    mongodb = os.environ.get("MONGODB_DATABASE", "smug")
    write_buffer_size = int(os.environ.get("MONGODB_WRITE_BUFFER", 100))
    prefetch_count = int(os.environ.get("PREFETCH_COUNT", 500))

    if write_buffer_size > prefetch_count:
        raise ValueError('MongoDB write buffer should not exceed prefetch count. This will cause the')

    mongo_save = MongoSave(write_buffer_size=write_buffer_size)
    watchdog = MongoSaveWatchdog(callback=mongo_save.save, threshold=1)
    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_queue('save', mongo_save.callback)
