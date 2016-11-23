# Load the on-time parquet file
on_time_dataframe = sqlContext.read.parquet('data/on_time_performance.parquet')

# The first step is easily expressed as SQL: get all unique tail numbers for each airline
on_time_dataframe.registerTempTable("on_time_performance")
carrier_codes = sqlContext.sql(
  "SELECT DISTINCT Carrier FROM on_time_performance"
  )
carrier_codes.collect()

airlines = sqlContext.read.format('com.databricks.spark.csv')\
  .options(header='false', nullValue='\N')\
  .load('data/airlines.csv')
airlines.show()

# Is Delta around?
airlines.filter(airlines.C3 == 'DL').show()

# Drop fields except for C1 as name, C3 as carrier code
airlines.registerTempTable("airlines")
airlines = sqlContext.sql("SELECT C1 AS Name, C3 AS CarrierCode from airlines")

# Join our 14 carrier codes to the airliens table to get our set of airlines
our_airlines = carrier_codes.join(airlines, carrier_codes.Carrier == airlines.CarrierCode)
our_airlines = our_airlines.select('Name', 'CarrierCode')
our_airlines.show()

# Store as JSON objects via a dataframe. Repartition to 1 to get 1 json file.
our_airlines.repartition(1).write.json("data/our_airlines.json")

#wikidata = sqlContext.read.json('data/wikidata-20160404-all.json.bz2')
