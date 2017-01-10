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

# flights -> airports @ time -> stations @ time

from pyspark.sql.functions import col, udf, lit, concat

# Convert station time to ISO time
def crs_time_to_iso(station_time):
  hour = station_time[0:2]
  minute = station_time[2:4]
  iso_time = "{hour}:{minute}:00".format(
    hour=hour,
    minute=minute
  )
  return iso_time

extract_time_udf = udf(crs_time_to_iso, StringType())

trimmed_flights = on_time_dataframe.select(
  "FlightNum",
  concat("FlightDate", lit("T"), extract_time_udf("CRSDepTime")).alias("CRSDepDatetime"),
  concat("FlightDate", lit("T"), extract_time_udf("CRSArrTime")).alias("CRSArrDatetime"),
  "FlightDate",
  "Origin",
  "Dest",
)

import iso8601
from datetime import timedelta
def increment_arrival_date(departure, arrival):
  """Handle overnight flights by incrementing the arrival date if a flight arrives earlier than it leaves"""
  d_dt = iso8601.parse_date(departure)
  a_dt = iso8601.parse_date(arrival)
  if a_dt.time() < d_dt.time():
    a_dt = a_dt + timedelta(days=1)
  return a_dt.isoformat()

increment_arrival_udf = udf(increment_arrival_date, StringType())

fixed_trimmed_flights = trimmed_flights.select(
  "FlightNum",
  "CRSDepDatetime",
  increment_arrival_udf("CRSDepDatetime", "CRSArrDatetime").alias("CRSArrDatetime"),
  "FlightDate",
  "Origin",
  "Dest"
)

# Join and get the origin WBAN ID
flights_with_origin_station = fixed_trimmed_flights.join(
  closest_stations,
  trimmed_flights.Origin == closest_stations.Airport
)
flights_with_origin_station = flights_with_origin_station.select(
  "FlightNum",
  "CRSDepDatetime",
  "CRSArrDatetime",
  "FlightDate",
  "Origin",
  "Dest",
  col("WBAN_ID").alias("Origin_WBAN_ID")
)

# Join and get the destination WBAN ID
flights_with_dest_station = flights_with_origin_station.join(
  closest_stations,
  flights_with_origin_station.Dest == closest_stations.Airport
)
flights_with_both_stations = flights_with_dest_station.select(
  "FlightNum",
  "CRSDepDatetime",
  "CRSArrDatetime",
  "FlightDate",
  "Origin",
  "Dest",
  "Origin_WBAN_ID",
  col("WBAN_ID").alias("Dest_WBAN_ID")
)

# Daily observation groupings
daily_station_observations_raw = sc.textFile("data/daily_station_observations.json")
import json
daily_station_observations = daily_station_observations_raw.map(json.loads)


from frozendict import frozendict
joinable_departure = flights_with_both_stations\
  .rdd\
  .repartition(3)\
  .map(
    lambda row: (
      frozendict({
        'Origin_WBAN_ID': row.Origin_WBAN_ID,  # compound key
        'CRSDepDate': row.CRSDepDate,
      }),
      row
    )
  )

