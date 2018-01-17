import pika
from pika.credentials import PlainCredentials
import os
import json
import pkg_resources
from dotenv import load_dotenv
import sys


def try_parse_json(json_text: str):
    if not json_text.startswith('{'):
        return json_text
    try:
        return json.loads(json_text)
    except json.JSONDecodeError:
        return json_text


env_location = pkg_resources.resource_filename('resources', '.env')

if os.environ.get('DOTENV_LOADED', '0') != '1':
    load_dotenv(env_location)

exchanges = {k[18:].lower(): try_parse_json(v)
             for k, v in os.environ.items()
             if k.startswith('RABBITMQ_EXCHANGE_')}
queues = {k[15:].lower(): try_parse_json(v)
          for k, v in os.environ.items()
          if k.startswith('RABBITMQ_QUEUE_')}


class ConnectionManager:
    """
    This manager handles all things related to RabbitMQ. Using this class one can connect to a RabbitMQ instance and
    not have to remake this code in every other class which needs connection to RabbitMQ.

    This class starts a blocking connection meaning that it will keep the connection open as long as the class exists.
    By default the connection manager will connect to the `vhost` `/` and on `port` `5672`

    Args:
        username (str, optional):
            The username which is used to connect to the RabbitMQ node. If none is provide it will be
            fetched from the environment file.
        password (str, optional):
            The password which is used to connect to the RabbitMQ node. If none is provide it will be
            fetched from the environment file.
        url (str, optional):
            The url which is used to connect to the RabbitMQ node. If none is provide it will be
            fetched from the environment file.
        prefetch_count(int, optional):
            The number of unacknowledged messages a worker can except. This is a natural way of
            spreading load between workers. If None is provided it will be fetched from the environment file.


    Note:
        The recommended value for `prefetch_count` is around 500 since this maximises performance when using both a
        single worker and multiple different workers.
    """

    def __init__(self, username: str = "", password: str = "", url: str = "", prefetch_count: int = -2):
        if 'sphinx' in sys.modules:
            return # don't load when sphinx is running
        if username == "":
            username = os.environ.get("RABBITMQ_DEFAULT_USER")
        if password == "":
            password = os.environ.get("RABBITMQ_DEFAULT_PASS")
        if url == "":
            url = os.environ.get("RABBITMQ_URL", "localhost")
        if prefetch_count == -2:
            self.prefetch_count = int(os.environ.get("PREFETCH_COUNT", 500))

        credentials = PlainCredentials(username=username, password=password)

        virtual_host = os.environ.get("RABBITMQ_DEFAULT_VHOST")
        params = pika.ConnectionParameters(host=url, port=5672, virtual_host=virtual_host, credentials=credentials,
                                           connection_attempts=10, retry_delay=10)

        self.connection = pika.BlockingConnection(parameters=params)
        self.channel = self.connection.channel()

    def publish_to_queue(self, queue_type: str, message: str):
        """
        Sends a message to a queue.

        Args:
            queue_type (str): The queue to send the message to. The actual queue name will be fetched based on the
                queue name provided by the ``get_queue_name`` function.
            message (str): The message to publish to the queue.

        """
        channel_name = self.get_queue_name(queue_type)
        self.channel.basic_publish(exchange='', routing_key=channel_name, body=message)

    def _subscribe(self, queue_type: str, callback: callable):
        """
        Subscribes to a queue and starts consuming. When a new message is received the callback will be executed.

        Args:
            queue_type (str): The queue to subscribe to.The actual queue name will be fetched based on the
                queue name provided by the ``get_queue_name`` function.
            callback (function): The function to execute upon receiving a message.

        Note:
            This is a private function and should not be used directly.
            Use the ``subscribe_to_queue`` function instead
        """
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(callback, queue_type)
        self.channel.start_consuming()

    def subscribe_to_queue(self, queue_type: str, callback: callable):
        """
        Subscribe to a queue. Once a message is received it wil be passed to the callback which will then be executed.
        Uses the ``_subscribe`` function underwater.

        Examples:
            >>> def callback(ch, method, properties, body):
            >>>     print('Got message {}'.format(body))
            >>> # Create a connection manager and subscribe to the test queue
            >>> connection_manager = ConnectionManager()
            >>> connection_manager.subscribe_to_queue('clean', callback)
            >>> # Send a message to test the callback is working.
            >>> connection_manager.publish_to_queue('clean', 'test')
            'Got message test'

        Args:
            queue_type: The queue to subscribe to.The actual queue name will be fetched based on the
                queue name provided by the ``get_queue_name`` function.
            callback: The function to execute upon receiving a message.
        """
        queue_type = self.get_queue_name(queue_type)
        self._subscribe(queue_type, callback)

    @staticmethod
    def get_queue_name(queue_type: str):
        """
        Returns the channel name for the provided queue_type. The queue name is fetched from the ``queues``
        variable.

        Examples:
            >>> queues = {
            >>>     'clean': "1_clean",
            >>>     'preprocess': "2_preprocess",
            >>>     'process_wordvec': json.loads('{"name":"3_process_wordvec","exchange":"3_process"}'),
            >>>     'process_location': json.loads('{"name":"3_process_location","exchange":"3_process"}'),
            >>>     'save': '4_save',
            >>> }
            >>> ConnectionManager.get_queue_name('clean')
            '1_clean'
            >>> ConnectionManager.get_queue_name('process_wordvec')
            '3_process_wordvec'
            >>> ConnectionManager.get_queue_name('non_existing_queue')
            KeyError: 'non_existing_queue'

        Args:
            queue_type (str): The queue_type you want to get the name from. Name will be resolved using the ``queues``
                variable.

        Returns:
            str: `queue_name` if successful

            If the `queue_type` is present in ``queues`` returns the corresponding queue name.
            If the queue_type is one with a exchange binding returns the name.

        Raises:
            KeyError: the provided `queue_type` is not present in ``queues``

        """
        queue = queues[queue_type]
        return queue['name'] if isinstance(queue, dict) else queue

    @staticmethod
    def get_queues():
        """
        Get's all the queues in the ``queues`` variable

        Returns:
            dict: returns the queue dict.

        """
        return queues

    @staticmethod
    def get_exchanges():
        """
        Get's all the exchanges in the ``exchanges`` variable

        Returns:
           dict: returns the exchanges dict.
        """
        return exchanges

    @staticmethod
    def get_exchange_name(exchange_type):
        """
        Returns the name of the provided exchange type. Is resolved by the ``exchanges`` variable

        Examples:
            >>> exchanges = {
            >>>     'process': {'name': '3_process', 'type': 'fanout'}
            >>> }
            >>> ConnectionManager.get_exchange_name('process')
            '3_process'
            >>> ConnectionManager.get_queue_name('non_existing_exchange')
            KeyError: 'non_existing_exchange'

        Args:
            exchange_type: The exchange_type you want to get the name from. Name will be resolved using the ``exchanges``
                variable.

        Returns:
            str: Returns the name corresponding to the `exchange_type`

        Raises:
            KeyError: the provided `exchange_type` is not present in ``exchanges``
        """
        return exchanges[exchange_type]['name']
