# PYSPARK_DRIVER_PYTHON=ipython pyspark --packages com.databricks:spark-csv_2.10:1.4.0

# Load the on-time parquet file
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')
on_time_dataframe.registerTempTable("on_time_performance")

from pyspark.sql.types import StringType, IntegerType, DoubleType
from pyspark.sql.types import StructType, StructField

wban_schema = StructType([
  StructField("REGION", StringType(), True),
  StructField("WBAN_ID", StringType(), True),
  StructField("STATION_NAME", StringType(), True),
  StructField("STATE_PROVINCE", StringType(), True),
  StructField("COUNTY", StringType(), True),
  StructField("COUNTRY", StringType(), True),
  StructField("EXTENDED_NAME", StringType(), True),
  StructField("CALL_SIGN", StringType(), True),
  StructField("STATION_TYPE", StringType(), True),
  StructField("DATE_ASSIGNED", StringType(), True),
  StructField("BEGIN_DATE", StringType(), True),
  StructField("COMMENTS", StringType(), True),
  StructField("LOCATION", StringType(), True),
  StructField("ELEV_OTHER", StringType(), True),
  StructField("ELEV_GROUND", StringType(), True),
  StructField("ELEV_RUNWAY", StringType(), True),
  StructField("ELEV_BAROMETRIC", StringType(), True),
  StructField("ELEV_STATION", StringType(), True),
  StructField("ELEV_UPPER_AIR", StringType(), True)
])

# Load the WBAN station master list
wban_master_list = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='false', delimiter='|')\
  .schema(wban_schema)\
  .load('data/wbanmasterlist.psv')
wban_master_list.show(5)

# Filter to only airports
airport_wbans = wban_master_list.filter(
  wban_master_list.STATION_NAME.endswith("AIRPORT")
)
airport_wbans.count() # 338

#
# Compare to airport count in on-time-performance table
#

# Get the airports from the origin/destination
origin_airports = spark.sql("""
SELECT Origin AS Airport
FROM on_time_performance
""")
dest_airports = spark.sql("""
SELECT Dest AS Airport
FROM on_time_performance
""")

# Combine the airports into one relation & sqlize it
all_airports_flights = origin_airports.union(dest_airports)
all_airports_flights.registerTempTable("all_airports_flights")

# Get the set of unique airport codes
distinct_airports = spark.sql("""
SELECT DISTINCT(Airport) FROM all_airports_flights
""")

# Get a count of the airport codes
distinct_airports.count() # 332

# Load the weather records themselves
hourly_weather_records = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true', delimiter=',')\
  .load('data/2015*hourly.txt')
hourly_weather_records.show()

# Show a few fields for a period for (probably) one station
trimmed_hourly_weather_records = hourly_weather_records.select(
  hourly_weather_records.WBAN,
  hourly_weather_records.Date,
  hourly_weather_records.Time,
  hourly_weather_records.SkyCondition,
  hourly_weather_records.WeatherType,
  hourly_weather_records.DryBulbCelsius,
  hourly_weather_records.Visibility,
  hourly_weather_records.WindSpeed,
  hourly_weather_records.WindDirection,
)
trimmed_hourly_weather_records.show()
