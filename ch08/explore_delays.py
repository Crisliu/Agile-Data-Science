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
on_time_heros = on_time_dataframe.filter((on_time_dataframe.DepDelayMinutes > 0) & (on_time_dataframe.ArrDelayMinutes <= 0))
total_on_time_heros = on_time_heros.count()

print "Total flights:   {}".format(total_flights)
print "Late departures: {}".format(total_late_departures)
print "Late arrivals:   {}".format(total_late_arrivals)
print "Recoveries:      {}".format(total_on_time_heros)
