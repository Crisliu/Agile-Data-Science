# If there is no SparkSession, create the environment...
# Note that this must be inserted IN your script. You can't import this, it won't work.
try:
  sc and spark
except NameError as e:
  
  import findspark
  
  findspark.init()
  import pyspark
  import pyspark.sql
  
  sc = pyspark.SparkContext()
  spark = pyspark.sql.SparkSession(sc).builder.appName("Agile Data Science").getOrCreate()
  
  # continue...
