# PYSPARK_DRIVER_PYTHON=ipython pyspark --packages com.databricks:spark-csv_2.10:1.4.0

# Load the on-time parquet file
on_time_dataframe = sqlContext.read.parquet('data/on_time_performance.parquet')

# Load the WBAN station master list
wban_master_list = sqlContext.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true', delimiter='|')\
  .load('data/wbanmasterlist.psv')
wban_master_list.show(5)

# Filter to only airports
airport_wbans = wban_master_list.filter(wban_master_list.STATION_NAME.endswith("AIRPORT"))
airport_wbans.count()

sqlContext.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true', delimiter=',')\
  .load('data/2015*daily.csv')
