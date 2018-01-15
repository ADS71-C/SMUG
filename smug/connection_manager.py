import pika
from pika.credentials import PlainCredentials
import os
import json
import pkg_resources
from dotenv import load_dotenv

queues = {}

exchanges = {}


def try_parse_json(json_text: str):
    if not json_text.startswith('{'):
        return json_text
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return json_text


class ConnectionManager:
    def __init__(self):
        global queues, exchanges
        env_location = pkg_resources.resource_filename('resources', '.env')
        load_dotenv(env_location)
        username = os.environ.get("RABBITMQ_DEFAULT_USER")
        password = os.environ.get("RABBITMQ_DEFAULT_PASS")
        url = os.environ.get("RABBITMQ_URL", "localhost")

        exchanges = {k[18:].lower(): try_parse_json(v)
                     for k, v in os.environ.items()
                     if k.startswith('RABBITMQ_EXCHANGE_')}
        queues = {k[15:].lower(): try_parse_json(v)
                  for k, v in os.environ.items()
                  if k.startswith('RABBITMQ_QUEUE_')}


        credentials = PlainCredentials(username=username, password=password)

        virtual_host = os.environ.get("RABBITMQ_DEFAULT_VHOST")
        params = pika.ConnectionParameters(host=url, port=5672, virtual_host=virtual_host, credentials=credentials)

        self.connection = pika.BlockingConnection(parameters=params)
        self.channel = self.connection.channel()
        self.prefetch_count = int(os.environ.get("PREFETCH_COUNT", 500))

    def publish_to_queue(self, queue_type, message):
        channel_name = self.get_queue_name(queue_type)
        self.channel.basic_publish(exchange='', routing_key=channel_name, body=message)

    def publish_to_exchange(self, routing_key, message, exchange='amq.direct'):
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)

    def _subscribe(self, queue_name, callback):
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(callback, queue_name)
        self.channel.start_consuming()

    def subscribe_to_queue(self, queue_name, callback):
        queue_name = self.get_queue_name(queue_name)
        self._subscribe(queue_name, callback)

    def subscribe_to_routing_key(self, routing_key, callback):
        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(queue_name, 'amq.direct', routing_key=routing_key)
        self._subscribe(queue_name, callback)

    @staticmethod
    def get_queue_name(channel_type):
        queue = queues[channel_type]
        return queue['name'] if isinstance(queue, dict) else queue

    @staticmethod
    def get_queues():
        return queues

    @staticmethod
    def get_exchanges():
        return exchanges

    @staticmethod
    def get_queue_names():
        return queues.values()

    @staticmethod
    def get_exchange_name(exchange_type):
        return exchanges[exchange_type]['name']
