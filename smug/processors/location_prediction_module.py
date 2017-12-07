import os
import pkg_resources
import json
import uuid
from bson import json_util

from mongo_manager import MongoManager
from smug.callback_helper import CallbackForward
from smug.connection_manager import ConnectionManager
from pyspark.sql import SparkSession
from src.algorithms import gmm


class LocationPredictionModule:
    def __init__(self):
        spark_url = os.environ.get("SPARK_URL", "local")
        spark = SparkSession \
            .builder \
            .master(spark_url) \
            .appName("Proftaak") \
            .getOrCreate()
        self.sc = spark.sparkContext
        self.mongo_manager = MongoManager()
        self.reports = [result for result in self.mongo_manager.get_reports()]
        model = pkg_resources.resource_filename('resources', 'location_prediction.csv')
        self.model = gmm.load_model(model)

    def gmm(self, message):
        tweet = self.sc.parallelize([message['message']])
        estimated_locations = gmm.predict_user_gmm(self.sc, tweet, [], self.model)
        message['reports'].append({
            'id': str(uuid.uuid4()),
            'estimate': estimated_locations
        })
        return message


@CallbackForward("save")
def callback(ch, method, properties, body):
    message = json.loads(body, object_hook=json_util.object_hook)
    return LocationPredictionModule.gmm(message)


if __name__ == '__main__':
    location_prediction_module = LocationPredictionModule()
    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_queue('process', callback)
