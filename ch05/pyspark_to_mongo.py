import pymongo_spark
# Important: activate pymongo_spark.
pymongo_spark.activate()

on_time_dataframe = sqlContext.read.json('../data/On_Time_On_Time_Performance_2015.jsonl.gz')
on_time_dataframe.saveToMongoDB('mongodb://localhost:27017/agile_data_science.on_time_performance')
