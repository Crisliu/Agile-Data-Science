#!/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils, OffsetRange, TopicAndPartition

# Pass date and base path to main() from airflow
def main(iso_date, base_path):

  APP_NAME = "make_predictions_streaming.py"

  # Process data every 10 seconds
  PERIOD = 10
  BROKERS = 'localhost:9092'
  PREDICTION_TOPIC = 'flight_delay_classification_request'
  
  try:
    sc and ssc
  except NameError as e:
  
    conf = SparkConf().set("spark.default.parallelism", 1)
    sc = SparkContext(appName="Agile Data Science: PySpark Streaming 'Hello, World!'", conf=conf)
    ssc = StreamingContext(sc, PERIOD)

  #
  # Load each and every model in the pipeline
  #

  # Load the arrival delay bucketizer
  from pyspark.ml.feature import Bucketizer
  arrival_bucketizer_path = "{}/models/arrival_bucketizer.bin".format(base_path)
  arrival_bucketizer = Bucketizer.load(arrival_bucketizer_path)

  # Load the departure delay bucketizer
  departure_bucketizer_path = "{}/models/departure_bucketizer.bin".format(base_path)
  departure_bucketizer = Bucketizer.load(departure_bucketizer_path)

  # Load all the string field vectorizer pipelines into a dict
  from pyspark.ml import PipelineModel

  string_vectorizer_pipeline_models = {}
  for column in ["Carrier", "DayOfMonth", "DayOfWeek", "DayOfYear",
                 "Origin", "Dest", "FlightNum", "DepDelayBucket"]:
    string_pipeline_model_path = "{}/models/string_indexer_pipeline_model_{}.bin".format(
      base_path,
      column
    )
    string_pipeline_model = PipelineModel.load(string_pipeline_model_path)
    string_vectorizer_pipeline_models[column] = string_pipeline_model

  # Load the numeric vector assembler
  from pyspark.ml.feature import VectorAssembler
  vector_assembler_path = "{}/models/numeric_vector_assembler.bin".format(base_path)
  vector_assembler = VectorAssembler.load(vector_assembler_path)

  # Load the final assembler
  final_assembler_path = "{}/models/final_vector_assembler.bin".format(base_path)
  final_assembler = VectorAssembler.load(final_assembler_path)

  # Load the classifier model
  from pyspark.ml.classification import RandomForestClassifier, RandomForestClassificationModel
  random_forest_model_path = "{}/models/spark_random_forest_classifier.flight_delays.bin".format(
    base_path
  )
  rfc = RandomForestClassificationModel.load(
    random_forest_model_path
  )
  
  #
  # Process Prediction Requests in Streaming
  #
  
  stream = KafkaUtils.createDirectStream(
    ssc,
    [PREDICTION_TOPIC],
    {
      "metadata.broker.list": BROKERS,
      "group.id": "0",
    }
  )

  object_stream = stream.map(lambda x: json.loads(x[1]))
  object_stream.pprint()

  ssc.start()
