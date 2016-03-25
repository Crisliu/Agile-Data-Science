# Run me with:
#
# IPYTHON=1 pyspark --jars ../lib/mongo-hadoop-spark-1.5.1.jar,../lib/mongo-java-driver-3.2.2.jar,../lib/mongo-hadoop-1.5.1.jar \
# --driver-class-path ../lib/mongo-hadoop-spark-1.5.1.jar:../lib/mongo-java-driver-3.2.2.jar:../lib/mongo-hadoop-1.5.1.jar

# configuration for output to MongoDB
config = {"mongo.output.uri": "mongodb://localhost:27017/agile_data_science.executives"}
outputFormatClassName = "com.mongodb.hadoop.MongoOutputFormat"

import pymongo
import pymongo_spark
# Important: activate pymongo_spark.
pymongo_spark.activate()

csv_lines = sc.textFile("example.csv")
data = csv_lines.map(lambda line: line.split(","))
schema_data = data.map(lambda x: {'name': x[0], 'company': x[1], 'title': x[2]})
schema_data.saveToMongoDB('mongodb://localhost:27017/agile_data_science.executives')

