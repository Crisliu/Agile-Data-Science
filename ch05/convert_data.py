# Loads CSV with header parsing and type inference, in one line!
# Must use 'pyspark --packages com.databricks:spark-csv_2.10:1.4.0' for this to work
on_time_dataframe = sqlContext.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true')\
  .load('data/On_Time_On_Time_Performance_2015.csv.gz')
on_time_dataframe = on_time_dataframe.drop("") # drop empty column

# Save records as gzipped json lines
on_time_dataframe.toJSON()\
  .saveAsTextFile(
    'data/On_Time_On_Time_Performance_2015.jsonl.gz',
    'org.apache.hadoop.io.compress.GzipCodec'
  )

# View records on filesystem
# gunzip -c data/On_Time_On_Time_Performance_2015.jsonl.gz/part-00000.gz | head

# Load JSON records back
on_time_dataframe = sqlContext.read.json('data/On_Time_On_Time_Performance_2015.jsonl.gz')
on_time_dataframe.show()

# Save records using Parquet
on_time_dataframe.write.parquet("data/on_time_performance.parquet")

# Load the parquet file
on_time_dataframe = sqlContext.read.parquet('data/on_time_performance.parquet')
