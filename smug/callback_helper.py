import simplejson as json
from functools import wraps
from smug.connection_manager import ConnectionManager
from bson import json_util


class CallbackForward:
    """
    Forward the result of a message after processing to another queue.

    It will not forward when:
        - the result is None
        - forward_channel_type is None

    Examples:
        >>> @CallbackForward("next_channel_name")
        >>> def some_handler(channel, method, properties, body):
        >>>     result = do_something(body)
        >>>     return result
        This example handles the incoming message from RabbitMQ in the do_something method.
        After the method has returned a result, it is returned by this method.
        CallbackForward will then forward the result to the channel named forward_channel_type.

    Args:
        forward_channel_type (str): The channel to forward to. This is looked up in ``ConnectionManager.get_queue_name``
    """
    def __init__(self, forward_channel_type=None):
        if forward_channel_type is not None:
            self.forward_channel = ConnectionManager.get_queue_name(forward_channel_type)
        else:
            self.forward_channel = forward_channel_type

    def __call__(self, func):
        """
        Actually wrap the method it self. It wraps func in the inner wrapped_callback method. And returns this method.

        Args:
            func: The function to wrap

        Returns:
            The wrapped function
        """
        outer_self = self

        @wraps(func)
        def wrapped_callback(channel, method, properties, body):
            result = func(channel, method, properties, body)

            if result is not None and outer_self.forward_channel is not None:
                message = json.dumps(result, default=json_util.default)
                channel.basic_publish(exchange='', routing_key=outer_self.forward_channel, body=message)

            channel.basic_ack(delivery_tag=method.delivery_tag)
        return wrapped_callback


class CallbackExchangeForward:
    """
    Forward the result of a message after processing to another exchange.

    It will not forward when:
        - the result is None
        - forward_exchange_type is None

    Examples:
        >>> @CallbackForward("next_channel_name")
        >>> def some_handler(channel, method, properties, body):
        >>>     result = do_something(body)
        >>>     return result
        This example handles the incoming message from RabbitMQ in the do_something method.
        After the method has returned a result, it is returned by this method.
        CallbackExchangeForward will then forward the result to the exchange named forward_exchange_type.

    Args:
        forward_exchange_type (str): The channel to forward to. This is looked up in ``ConnectionManager.get_queue_name``
    """
    def __init__(self, forward_exchange_type=None):
        if forward_exchange_type is not None:
            self.forward_exchange = ConnectionManager.get_exchange_name(forward_exchange_type)
        else:
            self.forward_exchange = forward_exchange_type

    def __call__(self, func):
        outer_self = self

        @wraps(func)
        def wrapped_callback(channel, method, properties, body):
            result = func(channel, method, properties, body)

            if result is not None and outer_self.forward_exchange is not None:
                message = json.dumps(result, default=json_util.default)
                channel.basic_publish(exchange=outer_self.forward_exchange, routing_key='', body=message)

            channel.basic_ack(delivery_tag=method.delivery_tag)
        return wrapped_callback
