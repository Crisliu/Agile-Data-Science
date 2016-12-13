#!/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

# Pass date and base path to main() from airflow
def main(iso_date, base_path):

  APP_NAME = "make_predictions.py"
  
  # If there is no SparkSession, create the environment
  try:
    sc and spark
  except NameError as e:
    import findspark
    findspark.init()
    import pyspark
    import pyspark.sql
    
    sc = pyspark.SparkContext()
    spark = pyspark.sql.SparkSession(sc).builder.appName(APP_NAME).getOrCreate()
  
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
  rfc = RandomForestClassificationModel.load("models/spark_random_forest_classifier.flight_delays.bin")
  
  #
  # Run the requests through the transformations from training
  #
  
  # Get today and tomorrow's dates as iso strings to scope query
  today_dt = iso8601.parse_date(iso_date)
  rounded_today = today_dt.date()
  iso_today = rounded_today.isoformat()

  # Build the day's input path: a date based primary key directory structure
  today_input_path = "{}/data/prediction_tasks_daily.json/{}".format(
    base_path,
    iso_today
  )

  from pyspark.sql.types import StringType, IntegerType, DoubleType, DateType, TimestampType
  from pyspark.sql.types import StructType, StructField

  schema = StructType([
    StructField("Carrier", StringType(), True),
    StructField("DayOfMonth", IntegerType(), True),
    StructField("DayOfWeek", IntegerType(), True),
    StructField("DayOfYear", IntegerType(), True),
    StructField("DepDelay", DoubleType(), True),
    StructField("Dest", StringType(), True),
    StructField("Distance", DoubleType(), True),
    StructField("FlightDate", DateType(), True),
    StructField("FlightNum", StringType(), True),
    StructField("Origin", StringType(), True),
    StructField("Timestamp", TimestampType(), True),
  ])
  
  prediction_requests = spark.read.json(today_input_path, schema=schema)
  prediction_requests.show()
  
  # Bucketize the departure and arrival delays for classification
  ml_bucketized_features = departure_bucketizer.transform(prediction_requests)

  # Check the buckets
  ml_bucketized_features.select("DepDelay", "DepDelayBucket").show()
  
  # Vectorize string fields with the corresponding pipeline for that column
  # Turn category fields into categoric feature vectors, then drop intermediate fields
  for column in ["Carrier", "DayOfMonth", "DayOfWeek", "DayOfYear",
                 "Origin", "Dest", "FlightNum", "DepDelayBucket"]:
    string_pipeline_path = "{}/models/string_indexer_pipeline_{}.bin".format(
      base_path,
      column
    )
    string_pipeline_model = string_vectorizer_pipeline_models[column]
    ml_bucketized_features = string_pipeline_model.transform(ml_bucketized_features)
    ml_bucketized_features = ml_bucketized_features.drop(column + "_index")
    
  # Vectorize numeric columns
  ml_bucketized_features = vector_assembler.transform(ml_bucketized_features)
  
  # Drop the original numeric columns
  numeric_columns = ["DepDelay", "Distance"]
  
  # Combine various features into one feature vector, 'features'
  final_vectorized_features = final_assembler.transform(ml_bucketized_features)
  final_vectorized_features.show()
  
  # Drop the individual vector columns
  feature_columns = ["Carrier_vec", "DayOfMonth_vec", "DayOfWeek_vec", "DayOfYear_vec",
                     "Origin_vec", "Dest_vec", "FlightNum_vec", "DepDelayBucket_vec",
                     "NumericFeatures_vec"]
  for column in feature_columns:
    final_vectorized_features = final_vectorized_features.drop(column)

  # Inspect the finalized features
  final_vectorized_features.show()
  
  # Make the prediction
  predictions = rfc.transform(final_vectorized_features)
  
  # Drop the features vector and prediction metadata to give the original fields
  predictions = predictions.drop("Features_vec")
  final_predictions = predictions.drop("indices").drop("values").drop("rawPrediction").drop("probability")
  
  # Inspect the output
  final_predictions.show()
  
  # Build the day's output path: a date based primary key directory structure
  today_output_path = "{}/data/prediction_results_daily.json/{}".format(
    base_path,
    iso_today
  )
  
  # Save the output to its daily bucket
  final_predictions.repartition(1).write.mode("overwrite").json(today_output_path)

if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
