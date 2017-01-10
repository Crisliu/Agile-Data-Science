base_path = "."

# Load the on-time parquet file
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')
on_time_dataframe.registerTempTable("on_time_performance")

from pyspark.sql.types import StringType, IntegerType, DoubleType
from pyspark.sql.types import StructType, StructField

# Load airports
airport_schema = StructType([
  StructField("AirportID", StringType(), True),
  StructField("Name", StringType(), True),
  StructField("City", StringType(), True),
  StructField("Country", StringType(), True),
  StructField("FAA", StringType(), True),
  StructField("ICAO", StringType(), True),
  StructField("Latitude", DoubleType(), True),
  StructField("Longitude", DoubleType(), True),
  StructField("Altitude", IntegerType(), True),
  StructField("Timezone", StringType(), True),
  StructField("DST", StringType(), True),
  StructField("TimezoneOlson", StringType(), True)
])
airports = spark.read.format('com.databricks.spark.csv')\
  .options(header='false', inferschema='false')\
  .schema(airport_schema)\
  .load("data/airports.csv")

# Load airport/station mappings
closest_stations_path = "{}/data/airport_station_pairs.json".format(
  base_path
)
closest_stations = spark.read.json(closest_stations_path)


