#
# Convert hourly weather PSV to Parquet format for improved performance
#

from pyspark.sql.types import StringType, IntegerType, DoubleType
from pyspark.sql.types import StructType, StructField

hourly_schema = StructType([
  StructField("WBAN", StringType(), True),
  StructField("Date", StringType(), True),
  StructField("Time", StringType(), True),
  StructField("StationType", StringType(), True),
  StructField("SkyCondition", StringType(), True),
  StructField("SkyConditionFlag", StringType(), True),
  StructField("Visibility", StringType(), True),
  StructField("VisibilityFlag", StringType(), True),
  StructField("WeatherType", StringType(), True),
  StructField("WeatherTypeFlag", StringType(), True),
  StructField("DryBulbFarenheit", StringType(), True),
  StructField("DryBulbFarenheitFlag", StringType(), True),
  StructField("DryBulbCelsius", StringType(), True),
  StructField("DryBulbCelsiusFlag", StringType(), True),
  StructField("WetBulbFarenheit", StringType(), True),
  StructField("WetBulbFarenheitFlag", StringType(), True),
  StructField("WetBulbCelsius", StringType(), True),
  StructField("WetBulbCelsiusFlag", StringType(), True),
  StructField("DewPointFarenheit", StringType(), True),
  StructField("DewPointFarenheitFlag", StringType(), True),
  StructField("DewPointCelsius", StringType(), True),
  StructField("DewPointCelsiusFlag", StringType(), True),
  StructField("RelativeHumidity", StringType(), True),
  StructField("RelativeHumidityFlag", StringType(), True),
  StructField("WindSpeed", StringType(), True),
  StructField("WindSpeedFlag", StringType(), True),
  StructField("WindDirection", StringType(), True),
  StructField("WindDirectionFlag", StringType(), True),
  StructField("ValueForWindCharacter", StringType(), True),
  StructField("ValueForWindCharacterFlag", StringType(), True),
  StructField("StationPressure", StringType(), True),
  StructField("StationPressureFlag", StringType(), True),
  StructField("PressureTendency", StringType(), True),
  StructField("PressureTendencyFlag", StringType(), True),
  StructField("PressureChange", StringType(), True),
  StructField("PressureChangeFlag", StringType(), True),
  StructField("SeaLevelPressure", StringType(), True),
  StructField("SeaLevelPressureFlag", StringType(), True),
  StructField("RecordType", StringType(), True),
  StructField("RecordTypeFlag", StringType(), True),
  StructField("HourlyPrecip", StringType(), True),
  StructField("HourlyPrecipFlag", StringType(), True),
  StructField("Altimeter", StringType(), True),
  StructField("AltimeterFlag", StringType(), True),
])

# Load the weather records themselves
hourly_weather_records = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='false', delimiter=',')\
  .schema(hourly_schema)\
  .load('data/2015*hourly.txt')
hourly_weather_records.show()

hourly_columns = ["WBAN", "Date", "Time", "SkyCondition",
                  "Visibility", "WeatherType", "DryBulbCelsius",
                  "WetBulbCelsius", "DewPointCelsius",
                  "RelativeHumidity", "WindSpeed", "WindDirection",
                  "ValueForWindCharacter", "StationPressure",
                  "SeaLevelPressure", "HourlyPrecip", "Altimeter"]

trimmed_hourly_records = hourly_weather_records.select(hourly_columns)

#
# Add an ISO8601 formatted ISODate column using DataFrame udfs
#
from pyspark.sql.functions import udf

# Convert station date to ISO Date
def station_date_to_iso(station_date):
  str_date = str(station_date)
  year = str_date[0:4]
  month = str_date[4:6]
  day = str_date[6:8]
  return "{}-{}-{}".format(year, month, day)

extract_date_udf = udf(station_date_to_iso, StringType())
hourly_weather_with_iso_date = trimmed_hourly_records.withColumn(
  "ISODate",
  extract_date_udf(trimmed_hourly_records.Date)
)

# Convert station time to ISO time
def station_time_to_iso(station_time):
  hour = station_time[0:2]
  minute = station_time[2:4]
  iso_time = "{hour}:{minute}:00".format(
    hour=hour,
    minute=minute
  )
  return iso_time

extract_time_udf = udf(station_time_to_iso, StringType())
hourly_weather_with_iso_time = hourly_weather_with_iso_date.withColumn(
  "ISOTime",
  extract_time_udf(trimmed_hourly_records.Time)
)

from pyspark.sql.functions import concat, lit
hourly_weather_with_iso_datetime = hourly_weather_with_iso_time.withColumn(
  "DateTime",
  concat(
    hourly_weather_with_iso_time.ISODate,
    lit("T"),
    hourly_weather_with_iso_time.ISOTime
  )
)

#
# Trim the final records, lose the original Date/Time fields and save
#
final_hourly_columns = ["WBAN", "DateTime", "SkyCondition",
                  "Visibility", "WeatherType", "DryBulbCelsius",
                  "WetBulbCelsius", "DewPointCelsius",
                  "RelativeHumidity", "WindSpeed", "WindDirection",
                  "ValueForWindCharacter", "StationPressure",
                  "SeaLevelPressure", "HourlyPrecip", "Altimeter"]
final_trimmed_hourly_records = hourly_weather_with_iso_datetime.select(
  final_hourly_columns
)
final_trimmed_hourly_records.show()

# Save cleaned up records using Parquet for improved performance
final_trimmed_hourly_records.write.mode("overwrite").parquet("data/2015_hourly_observations.parquet")

#
# Convert daily weather PSV to Parquet format for improved performance
#

# Load the weather records themselves
daily_schema = StructType([
  StructField("WBAN", StringType(), True),
  StructField("YearMonthDay", StringType(), True),
  StructField("Tmax", StringType(), True),
  StructField("TmaxFlag", StringType(), True),
  StructField("Tmin", StringType(), True),
  StructField("TminFlag", StringType(), True),
  StructField("Tavg", StringType(), True),
  StructField("TavgFlag", StringType(), True),
  StructField("Depart", StringType(), True),
  StructField("DepartFlag", StringType(), True),
  StructField("DewPoint", StringType(), True),
  StructField("DewPointFlag", StringType(), True),
  StructField("WetBulb", StringType(), True),
  StructField("WetBulbFlag", StringType(), True),
  StructField("Heat", StringType(), True),
  StructField("HeatFlag", StringType(), True),
  StructField("Cool", StringType(), True),
  StructField("CoolFlag", StringType(), True),
  StructField("Sunrise", StringType(), True),
  StructField("SunriseFlag", StringType(), True),
  StructField("Sunset", StringType(), True),
  StructField("SunsetFlag", StringType(), True),
  StructField("CodeSum", StringType(), True),
  StructField("CodeSumFlag", StringType(), True),
  StructField("Depth", StringType(), True),
  StructField("DepthFlag", StringType(), True),
  StructField("Water1", StringType(), True),
  StructField("Water1Flag", StringType(), True),
  StructField("SnowFall", StringType(), True),
  StructField("SnowFallFlag", StringType(), True),
  StructField("PrecipTotal", StringType(), True),
  StructField("PrecipTotalFlag", StringType(), True),
  StructField("StnPressure", StringType(), True),
  StructField("StnPressureFlag", StringType(), True),
  StructField("SeaLevel", StringType(), True),
  StructField("SeaLevelFlag", StringType(), True),
  StructField("ResultSpeed", StringType(), True),
  StructField("ResultSpeedFlag", StringType(), True),
  StructField("ResultDir", StringType(), True),
  StructField("ResultDirFlag", StringType(), True),
  StructField("AvgSpeed", StringType(), True),
  StructField("AvgSpeedFlag", StringType(), True),
  StructField("Max5Speed", StringType(), True),
  StructField("Max5SpeedFlag", StringType(), True),
  StructField("Max5Dir", StringType(), True),
  StructField("Max5DirFlag", StringType(), True),
  StructField("Max2Speed", StringType(), True),
  StructField("Max2SpeedFlag", StringType(), True),
  StructField("Max2Dir", StringType(), True),
  StructField("Max2DirFlag", StringType(), True),
])

daily_weather_records = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='false', delimiter=',')\
  .schema(daily_schema)\
  .load('data/2015*daily.txt')
daily_weather_records.show()