from smug.connection_manager import ConnectionManager
from smug.initializers.rabbitmq_initializer import RabbitMQInitializer
from smug.initializers.mongodb_initializer import MongoDBInitializer

if __name__ == '__main__':
    connection_manager = ConnectionManager()
    RabbitMQInitializer(connection_manager=connection_manager)
    MongoDBInitializer()
