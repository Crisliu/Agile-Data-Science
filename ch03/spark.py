csv_lines = sc.textFile("example.csv")
data = csv_lines.map(lambda line: line.split(","))



