# Loads CSV with header parsing and type inference, in one line!
# Must use 'pyspark --packages com.databricks:spark-csv_2.10:1.4.0' for this to work
on_time_dataframe = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true')\
.load('../data/On_Time_On_Time_Performance_2015.csv.gz')

# Check out the data - very wide so hard to see
on_time_dataframe.show()

# Use SQL to query data - what airport pairs have the most flights?
on_time_dataframe.registerTempTable("on_time_dataframe")

# Get the top route and global flight volumes
snow_bird_months = sqlContext.sql(
  "SELECT Month, Year, Origin, Dest, COUNT(*) AS total_flights FROM on_time_dataframe WHERE Origin IN ('LGA', 'LAX', 'SFO', 'JFK', 'ORD') AND Dest IN ('LGA', 'LAX', 'SFO', 'JFK', 'ORD') GROUP BY Origin, Dest, Year, Month ORDER BY Year, Month"
  )
total_flights_by_month = sqlContext.sql(
  "SELECT Month, Year, COUNT(*) AS total_flights FROM on_time_dataframe GROUP BY Year, Month ORDER BY Year, Month"
  )

# Convert from a count of flights to a ratio
snow_bird_months_totals = snow_bird_months.groupBy("Origin", "Dest").sum('total_flights')
snow_bird_months_with_total = snow_bird_months.join(snow_bird_months_totals)

snow_bird_months_with_total.map()

# Use dataflows
snow_bird_months.join(total_flights_by_month)

# We can go back and forth as we see fit!
