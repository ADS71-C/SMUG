import pika
from pika.credentials import PlainCredentials
import os
import json
import pkg_resources
from dotenv import load_dotenv

queues = {
    'format': os.environ.get("FORMATTING_QUEUE_NAME", "1_format"),
    'clean': os.environ.get("CLEANING_QUEUE_NAME", "2_clean"),
    'preprocess': os.environ.get("PREPROCESSING_QUEUE_NAME", "3_preprocess"),
    'process_wordvec': json.loads(os.environ.get("PROCESSING_QUEUE_WORDVEC_NAME",
                                                 '{"name":"4_process_wordvec","exchange":"4_process"}')),
    'process_location': json.loads(os.environ.get("PROCESSING_QUEUE_LOCATION_NAME",
                                                  '{"name":"4_process_location","exchange":"4_process"}')),
    'process_nlp': json.loads(os.environ.get("PROCESSING_QUEUE_NLP_NAME",
                                             '{"name":"4_process_nlp","exchange":"4_process"}')),
    'save': os.environ.get("SAVE_QUEUE_NAME", "5_save"),
}

exchanges = {
    'process': {'name': os.environ.get('PROCESSING_EXCHANGE_NAME', '4_process'), 'type': 'fanout'}
}


class ConnectionManager:
    def __init__(self):
        env_location = pkg_resources.resource_filename('resources', '.env')
        if os.environ.get('DOTENV_LOADED', '0') != '1':
            load_dotenv(env_location)
        username = os.environ.get("RABBITMQ_DEFAULT_USER")
        password = os.environ.get("RABBITMQ_DEFAULT_PASS")
        url = os.environ.get("RABBITMQ_URL", "localhost")

        credentials = PlainCredentials(username=username, password=password)

        virtual_host = os.environ.get("RABBITMQ_DEFAULT_VHOST")
        params = pika.ConnectionParameters(host=url, port=5672, virtual_host=virtual_host, credentials=credentials,
                                           connection_attempts=10, retry_delay=10)

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
