class RabbitMQInitializer:
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.channel_initialize()

    def channel_initialize(self):
        for queue in self.connection_manager.get_queue_names():
            durable = self.connection_manager.get_queue_name('save') in queue
            self.connection_manager.channel.queue_declare(queue=queue, durable=durable)
