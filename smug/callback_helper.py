import simplejson as json
from smug.connection_manager import ConnectionManager


class CallbackHelper:
    def __init__(self, callback, forward_channel_type=None):
        self.callback = callback
        if forward_channel_type is not None:
            self.forward_channel = ConnectionManager.get_queue_name(forward_channel_type)
        else:
            self.forward_channel = forward_channel_type

    def wrapped_callback(self, channel, method, properties, body):
        result = self.callback(channel, method, properties, body)

        if result is not None and self.forward_channel is not None:
            message = json.dumps(result)
            channel.basic_publish(exchange='', routing_key=self.forward_channel, body=message)

        channel.basic_ack(delivery_tag=method.delivery_tag)
