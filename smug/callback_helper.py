import simplejson as json
from functools import wraps
from smug.connection_manager import ConnectionManager
from bson import json_util


class CallbackForward:
    def __init__(self, forward_channel_type=None):
        if forward_channel_type is not None:
            self.forward_channel = ConnectionManager.get_queue_name(forward_channel_type)
        else:
            self.forward_channel = forward_channel_type

    def __call__(self, func):
        outer_self = self

        @wraps(func)
        def wrapped_callback(channel, method, properties, body):
            result = func(channel, method, properties, body)

            if result is not None and outer_self.forward_channel is not None:
                message = json.dumps(result, default=json_util.default)
                channel.basic_publish(exchange='', routing_key=outer_self.forward_channel, body=message)

            channel.basic_ack(delivery_tag=method.delivery_tag)
        return wrapped_callback
