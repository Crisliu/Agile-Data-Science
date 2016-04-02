# Load the parquet file
on_time_dataframe = sqlContext.read.parquet('../data/on_time_performance.parquet')

# Group flights by tail number
flights = on_time_dataframe.rdd.map(lambda x: (x.Carrier, x.FlightDate, x.FlightNum, x.TailNum))

flights = flights.filter(lambda x: x[3] == u'N001AA')

flights_per_airplane = flights\
  .map(lambda nameTuple: (nameTuple[3], [nameTuple[0:3]]))\
  .reduceByKey(lambda a, b: a + b)

