# Load the WBAN station master list
wban_master_list = sqlContext.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true', delimiter='|')\
  .load('data/wbanmasterlist.psv')
wban_master_list.show(5)

# Load the weather records themselves
hourly_weather_records = sqlContext.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true', delimiter=',')\
  .load('data/2015*hourly.txt')
hourly_weather_records.show()

def station_date_to_iso(station_date):
  str_date = str(station_date)
  year = str_date[0:4]
  month = str_date[4:6]
  day = str_date[6:8]
  return "{}-{}-{}".format(year, month, day)

# Group observations by station (WBAN) and Date...
# then gather a list of of hourly observations for that day
records_per_station_per_day = hourly_weather_records\
  .rdd\
  .map(
    lambda nameTuple: (
      (
        nameTuple.WBAN, # compound key
        station_date_to_iso(nameTuple.Date),
      ),
      [
        { # omit WBAN and Date
          'Time': nameTuple.Time,
          'SkyCondition': nameTuple.SkyCondition,
          'WeatherType': nameTuple.WeatherType,
          'DryBulbCelsius': nameTuple.DryBulbCelsius,
          'Visibility': nameTuple.Visibility,
          'WindSpeed': nameTuple.WindSpeed,
          'WindDirection': nameTuple.WindDirection,
        }
      ]
    )
  )\
  .reduceByKey(lambda a, b: a + b)\
  .map(lambda tuple:
    { # Compound key - WBAN and Date
      'WBAN': tuple[0][0],
      'Date': tuple[0][1],
      'Flights': sorted(
        tuple[1], key=lambda x: (x['Time'])
      ) # Sort by day/time
    }
  )
records_per_station_per_day.first()

# What do the WBAN IDs in both sets of records look like?
wbans_one = wban_master_list.select('WBAN_ID').distinct().sort('WBAN_ID')
wbans_one.show()
wbans_two = hourly_weather_records.select('WBAN').distinct().sort('WBAN')
wbans_two.show()

# Convert decimal to 5-digit 0 padded string
def wban_float_to_string(wban):
  return str(int(wban)).zfill(5)

# Test our wban function
wbans_one.rdd.map(lambda x: wban_float_to_string(x.WBAN_ID)).take(20)
wbans_two.rdd.map(lambda x: wban_float_to_string(x.WBAN)).take(20)

# Recompute our grouped weather observations using wban_float_to_string()
# ... and an RDD join requires (key, value), so make it so :)
records_per_station_per_day = hourly_weather_records\
  .rdd\
  .map(
    lambda nameTuple: (
      (
        wban_float_to_string(nameTuple.WBAN), # compound key
        station_date_to_iso(nameTuple.Date),
      ),
      [
        { # omit WBAN and Date
          'Time': nameTuple.Time,
          'SkyCondition': nameTuple.SkyCondition,
          'WeatherType': nameTuple.WeatherType,
          'DryBulbCelsius': nameTuple.DryBulbCelsius,
          'Visibility': nameTuple.Visibility,
          'WindSpeed': nameTuple.WindSpeed,
          'WindDirection': nameTuple.WindDirection,
        }
      ]
    )
  )\
  .reduceByKey(lambda a, b: a + b)\
  .map(lambda tuple: # An RDD join requires (key, value)
    ( # So we must nest our struct within a tuple
      tuple[0][0], # with a WBAN key
      {
        'WBAN': tuple[0][0],
        'Date': tuple[0][1],
        'Observations': sorted(
          tuple[1], key=lambda x: (x['Time'])
        ) # Sort by day/time
      }
    )
  )
records_per_station_per_day.first()

# Lets trim the wban master list to things we care about
trimmed_wban_master_list = wban_master_list.select(
  'WBAN_ID',
  'STATION_NAME',
  'STATE_PROVINCE',
  'COUNTRY',
  'EXTENDED_NAME',
  'CALL_SIGN',
  'STATION_TYPE',
  'LOCATION',
  'ELEV_GROUND',
)
trimmed_wban_master_list.show()

# Now make it into (key, value) tuple format
joinable_wban_master_list = trimmed_wban_master_list.rdd.map(
  lambda x:
    (
      wban_float_to_string(x.WBAN_ID),
      {
        'WBAN_ID': wban_float_to_string(x.WBAN_ID),
        'STATION_NAME': x.STATION_NAME,
        'STATE_PROVINCE': x.STATE_PROVINCE,
        'COUNTRY': x.COUNTRY,
        'EXTENDED_NAME': x.EXTENDED_NAME,
        'CALL_SIGN': x.CALL_SIGN,
        'STATION_TYPE': x.STATION_TYPE,
        'LOCATION': x.LOCATION,
        'ELEV_GROUND': x.ELEV_GROUND,
      }
    )
)
joinable_wban_master_list.take(1)

# Now we're ready to join...
station_profile_with_observations = records_per_station_per_day.join(joinable_wban_master_list)
station_profile_with_observations.take(1)

# Now transform this monstrosity into something we want to consume in Mongo...
def cleanup_joined_wbans(record):
  wban = record[0]
  join_record = record[1]
  observations = join_record[0]
  profile = join_record[1]
  return {
    'Profile': profile,
    'Date': observations['Date'],
    'WBAN': observations['WBAN'],
    'Observations': observations['Observations'],
  }

# pyspark.RDD.foreach() runs a function on all records in the RDD
cleaned_station_observations = station_profile_with_observations.map(cleanup_joined_wbans)
one_record = cleaned_station_observations.take(1)[0]

# Print it in a way we can actually see it
import json
print json.dumps(one_record, indent=2)

# Store the station/daily observation records to Mongo
import pymongo_spark
pymongo_spark.activate()
cleaned_station_observations.saveToMongoDB('mongodb://localhost:27017/agile_data_science.daily_station_observations')

