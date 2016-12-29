# Geopy will get the distance between pairs of lat/long
import geopy

base_path = "."

#
# Load our training data and count airports
#
from pyspark.sql.types import StringType, IntegerType, FloatType, DoubleType, DateType, TimestampType
from pyspark.sql.types import StructType, StructField
from pyspark.sql.functions import udf

schema = StructType([
  StructField("ArrDelay", DoubleType(), True),  # "ArrDelay":5.0
  StructField("CRSArrTime", TimestampType(), True),  # "CRSArrTime":"2015-12-31T03:20:00.000-08:00"
  StructField("CRSDepTime", TimestampType(), True),  # "CRSDepTime":"2015-12-31T03:05:00.000-08:00"
  StructField("Carrier", StringType(), True),  # "Carrier":"WN"
  StructField("DayOfMonth", IntegerType(), True),  # "DayOfMonth":31
  StructField("DayOfWeek", IntegerType(), True),  # "DayOfWeek":4
  StructField("DayOfYear", IntegerType(), True),  # "DayOfYear":365
  StructField("DepDelay", DoubleType(), True),  # "DepDelay":14.0
  StructField("Dest", StringType(), True),  # "Dest":"SAN"
  StructField("Distance", DoubleType(), True),  # "Distance":368.0
  StructField("FlightDate", DateType(), True),  # "FlightDate":"2015-12-30T16:00:00.000-08:00"
  StructField("FlightNum", StringType(), True),  # "FlightNum":"6109"
  StructField("Origin", StringType(), True),  # "Origin":"TUS"
])

features = spark.read.json(
  "data/simple_flight_delay_features.json",
  schema=schema
)
features.registerTempTable("features")

# Get the origins and dests into one relation and count the distinct codes
origins = features.select("Origin").alias("Airport")
dests = features.select("Dest").alias("Airport")
distinct_airports = origins.union(dests).distinct()
distinct_airports.count() # 322

#
# Load and inspect the Openflights airport database
#
from pyspark.sql.types import StringType, IntegerType, DoubleType
from pyspark.sql.types import StructType, StructField

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

# Show ATL
airports.filter(airports.FAA == "ATL").show()
airports.count() # 8107

#
# Check out the weather stations via the WBAN Master List
#

# Load the WBAN station master list
wban_master_list = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true', delimiter='|')\
  .load('data/wbanmasterlist.psv')
wban_master_list.count() # 7411

# How many have a location?
wban_with_location = wban_master_list.filter(
  wban_master_list.LOCATION != None
)
wban_with_location.count() # 1409
wban_with_location.select(
  "WBAN_ID",
  "STATION_NAME",
  "STATE_PROVINCE",
  "COUNTY",
  "COUNTRY",
  "CALL_SIGN",
  "LOCATION"
).show(10)

#
# Get the Latitude/Longitude of those stations with parsable locations
#
from pyspark.sql.functions import split
wban_with_lat_lon = wban_with_location.select(
  wban_with_location.WBAN_ID,
  (split(wban_with_location.LOCATION, ',')[0]).alias("Latitude"),
  (split(wban_with_location.LOCATION, ',')[1]).alias("Longitude")
)
wban_with_lat_lon.show(10)

# Count those that got a latitude and longitude
wban_with_lat_lon = wban_with_lat_lon.filter(
  wban_with_lat_lon.Longitude.isNotNull()
)
wban_with_lat_lon.count() # 393

#
# Extend the number of locations through geocoding
#

# Count the number of US WBANs
us_wbans = wban_master_list.filter("COUNTRY == 'US'")
us_wbans.count() # 4601

# Compose the addresses of US WBANs
us_wban_addresses = us_wbans.selectExpr(
  "WBAN_ID",
  "CONCAT(STATION_NAME, ', ', COALESCE(COUNTY, ''), ', ', STATE_PROVINCE, ', ', COUNTRY) AS Address"
)
us_wban_addresses.show(10, False)

non_null_us_wban_addresses = us_wban_addresses.filter(
  us_wban_addresses.Address.isNotNull()
)
non_null_us_wban_addresses.count() # 4597

# Try to geocode one record
from geopy.geocoders import Nominatim
geolocator = Nominatim()
geolocator.geocode("MARION COUNTY AIRPORT, MARION, SC, US")

# from socket import timeout
# from geopy.exc import GeocoderTimedOut
from pyspark.sql import Row

def get_location(record):
  geolocator = Nominatim()
  
  latitude = None
  longitude = None
  
  try:
    location = geolocator.geocode(record["Address"])
    if location:
      latitude = location.latitude
      longitude = location.longitude
  except:
    pass
  
  lat_lon_record = Row(
    WBAN_ID=record["WBAN_ID"],
    Latitude=latitude,
    Longitude=longitude,
    Address=record["Address"]
  )
  return lat_lon_record

# Geocode the the WBANs with addresses
wbans_geocoded = us_wban_addresses.rdd.map(get_location).toDF()

# Count the WBANs we encoded
non_null_wbans_geocoded = wbans_geocoded.filter(wbans_geocoded.Longitude.isNotNull())
non_null_wbans_geocoded.count() # 1,299
non_null_wbans_geocoded.show()

# Save the WBANs, they take a long time to compute
output_path = "{}/data/wban_address_with_lat_lon.json".format(base_path)
non_null_wbans_geocoded.repartition(1).write.mode("overwrite").json(output_path)

# Combine the original wban_with_lat_lon with our non_null_wbans_geocoded
trimmed_geocoded_wbans = non_null_wbans_geocoded.select(
  "WBAN_ID",
  "Latitude",
  "Longitude"
)
comparable_wbans = trimmed_geocoded_wbans\
  .union(wban_with_lat_lon)\
  .distinct()
comparable_wbans.count() # 1,692
comparable_wbans.show()

#
# Associate weather stations with airports
#

# Do a cartesian join to pair all
airport_wban_combinations = airports.rdd.cartesian(wban_with_location.rdd)

# Compare each pair of records
import sys
def airport_station_distance(record):
  try:
    airport = record[0]
    station = record[1]
    
    airport_lat = airport["Latitude"]
    airport_lon = airport["Longitude"]
    
    station_lat_lon = station["LOCATION"].split(",")
    station_lat = station_lat_lon[0].strip()
    station_lon = station_lat_lon[1].strip()
  
  except:
    return sys.maxsize
  
  
  
