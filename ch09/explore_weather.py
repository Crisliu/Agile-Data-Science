# Load the hourly observations
hourly_weather_records = spark.read.parquet("data/2015_hourly_observations.parquet")
hourly_weather_records.show()

# Group observations by station (WBAN) and Date...
# then gather a list of of hourly observations for that day
from frozendict import frozendict
records_per_station_per_day = hourly_weather_records\
  .repartition(1)\
  .rdd\
  .map(
    lambda row: (
      frozendict({
        'WBAN': row.WBAN, # compound key
        'Date': row.Date,
      }),
      [
        { # omit WBAN and Date
          'WBAN': row.WBAN,
          'Datetime': row.Datetime,
          'SkyCondition': row.SkyCondition,
          'Visibility': row.Visibility,
          'WeatherType': row.WeatherType,
          'DryBulbCelsius': row.DryBulbCelsius,
          'WetBulbCelsius': row.WetBulbCelsius,
          'DewPointCelsius': row.DewPointCelsius,
          'RelativeHumidity': row.RelativeHumidity,
          'WindSpeed': row.WindSpeed,
          'WindDirection': row.WindDirection,
          'ValueForWindCharacter': row.ValueForWindCharacter,
          'StationPressure': row.StationPressure,
          'SeaLevelPressure': row.SeaLevelPressure,
          'HourlyPrecip': row.HourlyPrecip,
          'Altimeter': row.Altimeter,
        }
      ]
    )
  )\
  .reduceByKey(lambda a, b: a + b)\
  .map(lambda tuple:
    { # Compound key - WBAN and Date
      'WBAN': tuple[0]['WBAN'],
      'Date': tuple[0]['Date'],
      # Sort observations by day/time
      'Observations': sorted(
        tuple[1], key=lambda x: x['Datetime']
      )
    }
  )

# Store and load, as it is expensive to compute
import json
per_day_output = "data/observations_per_station_per_day.json"
records_per_station_per_day\
  .map(json.dumps)\
  .saveAsTextFile(per_day_output)
records_per_station_per_day = sc\
  .textFile(per_day_output)\
  .map(json.loads)

records_per_station_per_day.first()

# Load the WBAN station master list
wban_master_list = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true', delimiter='|')\
  .load('data/wbanmasterlist.psv')
wban_master_list.show(5)

# What do the WBAN IDs in both sets of records look like?
wbans_one = wban_master_list.select('WBAN_ID').distinct().sort('WBAN_ID')
wbans_one.show()
wbans_two = hourly_weather_records.select('WBAN').distinct().sort('WBAN')
wbans_two.show()

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
print(json.dumps(one_record, indent=2))

# Store the station/daily observation records to Mongo
import pymongo_spark
pymongo_spark.activate()
cleaned_station_observations.saveToMongoDB('mongodb://localhost:27017/agile_data_science.daily_station_observations')

