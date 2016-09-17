# Load the on-time parquet file
on_time_dataframe = sqlContext.read.parquet('data/on_time_performance.parquet')
on_time_dataframe.registerTempTable("on_time_performance")

# Select a few features of interest
simple_on_time_features = on_time_dataframe.select(
  'FlightNum',
  'FlightDate',
  'Carrier',
  'Origin',
  'Dest',
  'DepDelayMinutes',
  'ArrDelayMinutes',
)
simple_on_time_features.show()

# Filter nulls, they can't help us
filled_on_time_features = simple_on_time_features.filter(
  (simple_on_time_features.ArrDelayMinutes != None)
  &
  (simple_on_time_features.DepDelayMinutes != None)
)

# Explicitly sort the data and keep it sorted throughout. Leave nothing to chance.
sorted_features = filled_on_time_features.sort(
  filled_on_time_features.Carrier,
  filled_on_time_features.Origin,
  filled_on_time_features.Dest,
  filled_on_time_features.FlightNum,
  filled_on_time_features.ArrDelayMinutes,
  filled_on_time_features.DepDelayMinutes,
)

# Store as a single json file
sorted_features.repartition(1).write.mode("overwrite").json("data/simple_flight_delay_features.json")
