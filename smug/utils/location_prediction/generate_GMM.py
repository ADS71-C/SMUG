import os
import pkg_resources
from dotenv import load_dotenv
from pyspark.sql import SparkSession

if __name__ == '__main__':
    env_location = pkg_resources.resource_filename('resources', '.env')
    load_dotenv(env_location)

    spark_url = os.environ.get("SPARK_URL", "localhost")
    spark = SparkSession \
        .builder \
        .master(spark_url) \
        .appName("Proftaak") \
        .getOrCreate()

    sc = spark.sparkContext

    # Share the soft-boiled library with the cluster
    soft_boiled = pkg_resources.resource_filename('resources', 'soft-boiled.zip')
    sc.addPyFile(soft_boiled)
    from src.algorithms import gmm

    # Load the train data in chunks and filter tweets with a location.
    tweets_df = None
    for filename in os.listdir('train_dataset_small'):
        print(filename)
        chunk = spark.read.json('train_dataset_small/' + filename)
        chunk = chunk.filter('geo is not null')
        chunk = chunk.filter('place is not null')
        chunk = chunk.select(['user', 'text', 'geo', 'place', 'entities.urls', 'extended_entities.media'])
        if tweets_df is not None:
            tweets_df = tweets_df.union(chunk)
        else:
            tweets_df = chunk

    tweets_df.createOrReplaceTempView('my_tweets')

    # Train and create the model
    gmm_model = gmm.train_gmm(spark, 'my_tweets', ['user.location', 'text'], min_occurrences=5, max_num_components=12)

    # Save model for future prediction use
    path = pkg_resources.resource_filename('resources', 'location_prediction.csv')
    gmm.save_model(gmm_model, path)
