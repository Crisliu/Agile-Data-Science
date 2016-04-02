# Load the parquet file
on_time_dataframe = sqlContext.read.parquet('../data/on_time_performance.parquet')

# Use SQL to look at the total flights by month across 2015
total_flights_by_month = sqlContext.sql(
  "SELECT Month, Year, COUNT(*) AS total_flights FROM on_time_dataframe GROUP BY Year, Month ORDER BY Year, Month"
  )

# This map/asDict trick makes the rows print a little prettier. It is optional.
flights_chart_data = total_flights_by_month.map(lambda row: row.asDict())
flights_chart_data.collect()

# Save chart to MongoDB
import pymongo_spark
pymongo_spark.activate()
flights_chart_data.saveToMongoDB('mongodb://localhost:27017/agile_data_science.flights_by_month')

# Convert from a count of flights to a ratio
snow_bird_months_totals = snow_bird_months.groupBy("Origin", "Dest").sum('total_flights')
snow_bird_months_with_total = snow_bird_months.join(snow_bird_months_totals)

snow_bird_months_with_total.map()

# Use dataflows
snow_bird_months.join(total_flights_by_month)

# We can go back and forth as we see fit!
