import pika
from pika.credentials import PlainCredentials
import os
import pkg_resources
from dotenv import load_dotenv

queues = {
    'formatting': os.environ.get("FORMATTING_QUEUE_NAME", "formatting"),
    'cleaning': os.environ.get("CLEANING_QUEUE_NAME", "cleaning"),
    'preprocessing': os.environ.get("PREPROCESSING_QUEUE_NAME", "preprocessing"),
    'processing': os.environ.get("PROCESSING", "processing"),
    'save': os.environ.get("SAVE_QUEUE_NAME", "save"),

}


class ConnectionManager:
    def __init__(self):
        env_location = pkg_resources.resource_filename('resources', '.env')
        load_dotenv(env_location)
        username = os.environ.get("RABBITMQ_DEFAULT_USER")
        password = os.environ.get("RABBITMQ_DEFAULT_PASS")
        url = os.environ.get("RABBITMQ_URL", "localhost")

        credentials = PlainCredentials(username=username, password=password)
        params = pika.ConnectionParameters(host=url, port=5672, virtual_host="smug", credentials=credentials)

        self.connection = pika.BlockingConnection(parameters=params)
        self.channel = self.connection.channel()
        self.prefetch_count = int(os.environ.get("PREFETCH_COUNT", 500))

    def publish(self, channel_type, message):
        channel_name = self.get_queue_name(channel_type)

        self.channel.basic_publish(exchange='', routing_key=channel_name, body=message)

    def subscribe(self, channel_name, callback):
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(callback, self.get_queue_name(channel_name))
        self.channel.start_consuming()

    @staticmethod
    def get_queue_name(channel_type):
        return queues[channel_type]

    @staticmethod
    def get_queue_names():
        return queues.values()
