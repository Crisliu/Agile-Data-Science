csv_lines = sc.textFile("data/example.csv")

# Compute a histogram of departure delays
flattened_words = csv_lines\
  .map(lambda line: line.split(","))\
  .flatMap(lambda x: x)

flattened_words.collect()
