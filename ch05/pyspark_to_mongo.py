import json
import pymongo
import pymongo_spark
# Important: activate pymongo_spark.
pymongo_spark.activate()

config = {"mongo.output.uri": "mongodb://localhost:27017/agile_data_science.on_time_performance"}

on_time_lines = sc.textFile("../data/On_Time_On_Time_Performance_2015.jsonl.gz")
on_time_performance = on_time_lines.map(lambda x: json.loads(x))
on_time_performance.saveToMongoDB('mongodb://localhost:27017/agile_data_science.on_time_performance')

on_time_dataframe = sqlContext.read.parquet('../data/on_time_performance.parquet')
on_time_dataframe = on_time_dataframe.drop("")
on_time_dataframe.rdd.saveToMongoDB('mongodb://localhost:27017/agile_data_science.on_time_performance')

on_time_dataframe.rdd.saveAsNewAPIHadoopFile(
  path='file://unused', 
  outputFormatClass='com.mongodb.hadoop.MongoOutputFormat',
  keyClass='org.apache.hadoop.io.Text', 
  valueClass='org.apache.hadoop.io.MapWritable', 
  conf=config
)

on_time_dataframe.rdd.saveToMongoDB('mongodb://localhost:27017/agile_data_science.on_time_performance')

on_time_dataframe.rdd.saveToBSON('../data/on_time_performance.bson')
