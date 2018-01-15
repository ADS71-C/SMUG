import locale
from argparse import ArgumentParser

import pkg_resources
import json
from bson import json_util
import os
import tweepy
from dotenv import load_dotenv

from send_to_smug_helper import SendToSmugHelper
from smug.connection_manager import ConnectionManager


class StreamingListener(tweepy.StreamListener):
    def __init__(self):
        super().__init__()
        env_location = pkg_resources.resource_filename('resources', '.env')
        if os.environ.get('DOTENV_LOADED', '0') != '1':
            load_dotenv(env_location)
        consumer_token = os.environ.get("TWITTER_CONSUMER_TOKEN", "TOKEN")
        consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET", "SECRET")
        access_token = os.environ.get("TWITTER_ACCESS_TOKEN", "TOKEN")
        access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "SECRET")

        auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        stream = tweepy.Stream(auth=auth, listener=self)
        stream.filter(locations=[3.31497114423, 50.803721015, 7.09205325687, 53.5104033474])
        print(stream.running)

    @SendToSmugHelper()
    def on_status(self, original_message):
        if original_message.lang == 'nl':
            return {
                'message': original_message.text,
                'author': original_message.author.name,
                'metadata': {
                    'date': original_message.created_at,
                    'url': original_message.id,
                    'type': 'post',
                    'source': 'twitter',
                    'source_import': 'live_twitter',
                    'lang': locale.normalize('{}.utf-8'.format(original_message.lang))
                }
            }


if __name__ == '__main__':
    StreamingListener()
