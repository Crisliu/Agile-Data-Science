import pymongo
import pymongo_spark
# Important: activate pymongo_spark.
pymongo_spark.activate()

on_time_dataframe = sqlContext.read.parquet('../data/on_time_performance.parquet')

# Short form - note we have to convert the row to a dict to avoid https://jira.mongodb.org/browse/HADOOP-276
on_time_dataframe.rdd.map(lambda row: row.asDict()).saveToMongoDB('mongodb://localhost:27017/agile_data_science.on_time_performance')

# Long form - note we have to convert the row to a dict to avoid https://jira.mongodb.org/browse/HADOOP-276
on_time_dataframe.rdd.map(lambda row: row.asDict()).saveAsNewAPIHadoopFile(
  path='file://unused', 
  outputFormatClass='com.mongodb.hadoop.MongoOutputFormat',
  keyClass='org.apache.hadoop.io.Text', 
  valueClass='org.apache.hadoop.io.MapWritable', 
  conf={"mongo.output.uri": "mongodb://localhost:27017/agile_data_science.on_time_performance"}
)
