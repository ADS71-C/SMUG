import os
import pkg_resources
from pyspark.sql import SparkSession

if __name__ == '__main__':
    spark_url = os.environ.get("SPARK_URL", "local")
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

    # Load the test data in chunks and filter tweets with a location.
    tweets_df = None
    for filename in os.listdir('tds1'):
        print(filename)
        chunk = spark.read.json('tds1/' + filename)
        chunk = chunk.filter('geo is not null')
        chunk = chunk.filter('place is not null')
        chunk = chunk.select(['user', 'text', 'geo', 'place', 'entities.urls', 'extended_entities.media'])
        if tweets_df is not None:
            tweets_df = tweets_df.union(chunk)
        else:
            tweets_df = chunk

    tweets_df.createOrReplaceTempView('my_test_tweets')

    # Load the GMM model
    model = pkg_resources.resource_filename('resources', 'location_prediction.csv')
    gmm_model = gmm.load_model(model)

    # Test GMM model
    test_results = gmm.run_gmm_test(sc, spark, 'my_test_tweets', ['user.location', 'text'], gmm_model)
    print(test_results)
