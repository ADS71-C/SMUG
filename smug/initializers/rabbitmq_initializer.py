from connection_manager import ConnectionManager


class RabbitMQInitializer:
    def __init__(self, connection_manager=ConnectionManager()):
        self.connection_manager = connection_manager
        self.exchange_initialize()
        self.channel_initialize()

    def channel_initialize(self):
        for queue in self.connection_manager.get_queues().values():
            if isinstance(queue, dict):
                name = queue['name']
                exchange = queue['exchange']

                result = self.connection_manager.channel.queue_declare(queue=name)
                self.connection_manager.channel.queue_bind(exchange=exchange, queue=result.method.queue)
            else:
                durable = self.connection_manager.get_queue_name(
                    'save') in queue or self.connection_manager.get_queue_name('latest') in queue
                self.connection_manager.channel.queue_declare(queue=queue, durable=durable)

    def exchange_initialize(self):
        for exchange in self.connection_manager.get_exchanges().values():
            self.connection_manager.channel.exchange_declare(exchange=exchange['name'], exchange_type=exchange['type'])
