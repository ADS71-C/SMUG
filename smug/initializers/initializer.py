import os
import pkg_resources

from lib.dotenv import load_dotenv
from smug.connection_manager import ConnectionManager
from smug.initializers.rabbitmq_initializer import RabbitMQInitializer
from smug.initializers.mongodb_initializer import MongoDBInitializer

if __name__ == '__main__':
    env_location = pkg_resources.resource_filename('resources', '.env')
    if os.environ.get('DOTENV_LOADED', '0') != '1':
        load_dotenv(env_location)

    if 'RABBITMQ_URL' in os.environ:
        del os.environ['RABBITMQ_URL']
    if 'MONGO_URI' in os.environ:
        del os.environ['MONGO_URI']
    connection_manager = ConnectionManager()
    RabbitMQInitializer(connection_manager=connection_manager)
    MongoDBInitializer()
