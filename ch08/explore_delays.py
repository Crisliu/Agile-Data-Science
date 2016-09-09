# Load the on-time parquet file
on_time_dataframe = sqlContext.read.parquet('data/on_time_performance.parquet')
total_flights = on_time_dataframe.count()

# Flights that were late leaving...
late_departures = on_time_dataframe.filter(on_time_dataframe.DepDelayMinutes > 0)
total_late_departures = late_departures.count()

# Flights that were late arriving...
late_arrivals = on_time_dataframe.filter(on_time_dataframe.ArrDelayMinutes > 0)
total_late_arrivals = late_arrivals.count()

# Flights that left late but made up time to arrive on time...
on_time_heros = on_time_dataframe.filter(
  (on_time_dataframe.DepDelayMinutes > 0)
  &
  (on_time_dataframe.ArrDelayMinutes <= 0)
)
total_on_time_heros = on_time_heros.count()

# Get the percentage of flights that are late, rounded to 1 decimal place
pct_late = round((total_late_arrivals / (total_flights * 1.0)) * 100, 1)

print "Total flights:   {:,}".format(total_flights)
print "Late departures: {:,}".format(total_late_departures)
print "Late arrivals:   {:,}".format(total_late_arrivals)
print "Recoveries:      {:,}".format(total_on_time_heros)
print "Percentage Late: {}%".format(pct_late)

# Get the average minutes late
sqlContext.sql("SELECT ROUND(AVG(ArrDelayMinutes),1) FROM on_time_performance").show()

# Why are flights late? Lets look at a weather delayed flight
weather_delays = on_time_dataframe.filter(
  (on_time_dataframe.WeatherDelay != None)
  &
  (on_time_dataframe.WeatherDelay > 0)
)
weather_delays.select(
  weather_delays.Carrier,
  weather_delays.DepDelayMinutes,
  weather_delays.ArrDelayMinutes,
  weather_delays.WeatherDelay,
  weather_delays.CarrierDelay,
  weather_delays.NASDelay,
  weather_delays.SecurityDelay,
).show(1000)

on_time_dataframe.registerTempTable("on_time_performance")

# Calculate the percentage contribution to delay for each source
total_delays = sqlContext.sql("""
SELECT
  ROUND(SUM(WeatherDelay)/SUM(ArrDelayMinutes) * 100, 1) AS pct_weather_delay,
  ROUND(SUM(CarrierDelay)/SUM(ArrDelayMinutes) * 100, 1) AS pct_carrier_delay,
  ROUND(SUM(NASDelay)/SUM(ArrDelayMinutes) * 100, 1) AS pct_nas_delay,
  ROUND(SUM(SecurityDelay)/SUM(ArrDelayMinutes) * 100, 1) AS pct_security_delay
FROM on_time_performance
""")

# Generate a histogram of the weather and carrier delays
weather_delay_histogram = on_time_dataframe\
  .select("WeatherDelay")\
  .rdd\
  .flatMap(lambda x: x)\
  .histogram(10)

print "{}\n{}".format(weather_delay_histogram[0], weather_delay_histogram[1])

# Eyeball the first to define our buckets
weather_delay_histogram = on_time_dataframe\
  .select("WeatherDelay")\
  .rdd\
  .flatMap(lambda x: x)\
  .histogram([0, 15, 30, 60, 120, 240, 480, 720, 24*60.0])
print weather_delay_histogram

# Transform the data into something easily consumed by d3
record = {'key': 1, 'data': []}
for label, count in zip(weather_delay_histogram[0], weather_delay_histogram[1]):
  record['data'].append(
    {
      'label': label,
      'count': count
    }
  )

# Save to Mongo directly, since this is a Tuple not a dataframe or RDD
from pymongo import MongoClient
client = MongoClient()
client.relato.weather_delay_histogram.insert_one(record)

# Transform the data into something easily consumed by d3
def histogram_to_publishable(histogram):
  record = {'key': 1, 'data': []}
  for label, value in zip(histogram[0], histogram[1]):
    record['data'].append(
      {
        'label': label,
        'value': value
      }
    )
  return record

# Recompute the weather histogram with a filter for on-time flights
weather_delay_histogram = on_time_dataframe\
  .filter(
    (on_time_dataframe.WeatherDelay != None)
    &
    (on_time_dataframe.WeatherDelay > 0)
  )\
  .select("WeatherDelay")\
  .rdd\
  .flatMap(lambda x: x)\
  .histogram([0, 15, 30, 60, 120, 240, 480, 720, 24*60.0])
print weather_delay_histogram

record = histogram_to_publishable(weather_delay_histogram)
# Get rid of the old stuff and put the new stuff in its place
client.relato.weather_delay_histogram.drop()
client.relato.weather_delay_histogram.insert_one(record)
