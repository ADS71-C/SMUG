import os
import pkg_resources
import json
from bson import json_util

from mongo_manager import MongoManager
from smug.callback_helper import CallbackForward
from smug.connection_manager import ConnectionManager
from pyspark.sql import SparkSession
from src.algorithms import gmm

from pyspark.sql import Row
from collections import OrderedDict


def convert_to_row(d: dict) -> Row:
    return Row(**OrderedDict(sorted(d.items())))


class LocationPredictionModule:
    def __init__(self):
        spark_url = os.environ.get("local", "local")
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
        tweet = self.sc.parallelize([{'user': message['author'], 'text': message['message']}]).map(convert_to_row).toDF()
        estimated_locations = gmm.predict_user_gmm(self.sc, tweet, ['text', 'user'], self.model, radius=50.,
                                                   predict_lower_bound=0.2,  num_partitions=1).collect()
        print(estimated_locations)
        message['reports'].append({
            'id': 'Location Prediction',
            'estimate': estimated_locations
        })
        return message


@CallbackForward("save")
def callback(ch, method, properties, body):
    message = json.loads(body, object_hook=json_util.object_hook)
    return location_prediction_module.gmm(message)


if __name__ == '__main__':
    location_prediction_module = LocationPredictionModule()
    connection_manager = ConnectionManager()
    connection_manager.subscribe_to_queue('process_location', callback)
