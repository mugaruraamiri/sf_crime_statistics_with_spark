import logging
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as psf


# TODO Create a schema for incoming resources
schema = StructType([
    StructField("crime_id", StringType(), True),
    StructField("original_crime_type_name", StringType(), True),
    StructField("report_date", StringType(), True),
    StructField("call_date", StringType(), True),
    StructField("offense_date", StringType(), True),
    StructField("call_time", StringType(), True),
    StructField("call_date_time", StringType(), True),
    StructField("disposition", StringType(), True),
    StructField("address", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("agency_id", StringType(), True),
    StructField("address_type", StringType(), True),
    StructField("common_location", StringType(), True)
])

def run_spark_job(spark):

    # TODO Create Spark Configuration
    # Create Spark configurations with max offset of 200 per trigger
    # set up correct bootstrap server and port
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "com.police.service.calls") \
        .option("startingOffsets", "earliest") \
        .option("maxRatePerPartition", 100) \
        .option("maxOffsetPerTrigger", 100) \
        .option("stopGracefullyOnShutdown", "true") \
        .load()

    # Show schema for the incoming resources for checks
    df.printSchema()

    # TODO extract the correct column from the kafka input resources
    # Take only value and convert it to String
    kafka_df = df.selectExpr("CAST(value as STRING)")

    service_table = kafka_df\
        .select(psf.from_json(psf.col('value'), schema).alias("DF"))\
        .select("DF.*")
    #
    # # # TODO select original_crime_type_name and disposition
    distinct_table = service_table \
        .select(
            psf.col("original_crime_type_name"),
            psf.col("disposition"),
            psf.to_timestamp(psf.col("call_date_time")).alias("call_date_time")
        )
    distinct_table.printSchema()

    # # # count the number of original crime type

    agg_df = distinct_table \
        .select(
            psf.col("original_crime_type_name"),
            psf.col("disposition"),
            psf.col("call_date_time")
        ) \
        .withWatermark("call_date_time", "60 minutes") \
        .groupBy(
            psf.col("original_crime_type_name"),
            psf.col("disposition"),
            psf.col("call_date_time")
        ) \
        .count()
    #
    agg_df.printSchema()
    # #
    # # # TODO Q1. Submit a screen shot of a batch ingestion of the aggregation
    # # # TODO write output stream
    query = agg_df \
        .writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()
    # # #
    # # #
    # # # # TODO attach a ProgressReporter
    query.awaitTermination()
    # #
    # # TODO get the right radio code json path
    radio_code_json_filepath = "radio_code.json"
    radio_code_df = spark.read.json(radio_code_json_filepath, multiLine=True)

    radio_code_df.printSchema()
    #
    # # clean up your data so that the column names match on radio_code_df and agg_df
    # # we will want to join on the disposition code
    #
    # # TODO rename disposition_code column to disposition
    radio_code_df = radio_code_df.withColumnRenamed("disposition_code", "disposition")

    radio_code_df.printSchema()
    #
    # # TODO join on disposition column
    join_query = agg_df.join(radio_code_df, "disposition") \
        .writeStream \
        .format("console") \
        .queryName("join") \
        .start()
    #
    #
    join_query.awaitTermination()


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # TODO Create Spark in Standalone mode
    spark = SparkSession \
        .builder \
        .master("local[*]") \
        .appName("KafkaSparkStructuredStreaming") \
        .getOrCreate()

    spark.conf.set("spark.executor.memory", "8g")
    spark.conf.set("spark.executor.cores", "3")
    spark.conf.set('spark.cores.max', '3')
    spark.conf.set("spark.driver.memory", '8g')

    # spark.conf.set("spark.executor.memory", "3g")
    # spark.conf.set("spark.executor.cores", "2")
    # spark.conf.set('spark.cores.max', '2')
    # spark.conf.set("spark.driver.memory", '4g')


    logger.info("Spark started")

    run_spark_job(spark)

    spark.stop()
