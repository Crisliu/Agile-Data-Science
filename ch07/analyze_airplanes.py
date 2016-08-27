airplanes = sqlContext.read.json('data/airplanes.json')

#
# Who makes the airplanes in the US commercial fleet, as a %
#

# How many airplanes are made by each manufacturer?
airplanes.registerTempTable("airplanes")
manufacturer_counts = sqlContext.sql("""SELECT
  Manufacturer,
  COUNT(*) AS Total
FROM
  airplanes
GROUP BY
  Manufacturer
ORDER BY
  Total DESC"""
)
manufacturer_counts.show(30) # show top 30

# How many airplanes total?
total_airplanes = sqlContext.sql(
  """SELECT
  COUNT(*) AS OverallTotal
  FROM airplanes"""
)
print "Total airplanes: {}".format(total_airplanes.collect()[0].OverallTotal)

mfr_with_totals = manufacturer_counts.join(total_airplanes)
mfr_with_totals = mfr_with_totals.map(
  lambda x: {
    'Manufacturer': x.Manufacturer,
    'Total': x.Total,
    'Percentage': round(
      (
        float(x.Total)/float(x.OverallTotal)
      ) * 100,
      2
    )
  }
)
mfr_with_totals.toDF().show()

grouped_manufacturer_counts = manufacturer_counts.groupBy

# Save to Mongo in the airplanes_per_carrier relation
import pymongo_spark
pymongo_spark.activate()
manufacturer_counts.saveToMongoDB(
  'mongodb://localhost:27017/agile_data_science.manufacturer_counts'
)
