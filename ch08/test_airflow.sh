#!/bin/bash

# List DAGs
airflow list_dags

# List tasks in each DAG
airflow list_tasks agile_data_science_batch_prediction_model_training
airflow list_tasks agile_data_science_batch_predictions_daily

# Test each task in each DAG
airflow test agile_data_science_batch_prediction_model_training pyspark_extract_features 2016-12-12
airflow test agile_data_science_batch_prediction_model_training pyspark_train_classifier_model 2016-12-12

airflow test agile_data_science_batch_predictions_daily pyspark_fetch_prediction_requests 2016-12-12
airflow test agile_data_science_batch_predictions_daily pyspark_make_predictions 2016-12-12
airflow test agile_data_science_batch_predictions_daily pyspark_load_prediction_results 2016-12-12

# Test the training and persistence of the models
airflow backfill -s 2016-12-12 -e 2016-12-12 agile_data_science_batch_prediction_model_training

# Test the daily operation of the model
airflow backfill -s 2016-12-12 -e 2016-12-12 agile_data_science_batch_predictions_daily
