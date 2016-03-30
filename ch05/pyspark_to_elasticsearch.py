import json

on_time_lines = sc.textFile("../data/On_Time_On_Time_Performance_2015.jsonl.gz")
on_time_performance = on_time_lines.map(lambda x: json.loads(x))

# Format data for Elasticsearch, as a tuple with a dummy key in the first field
on_time_performance = on_time_performance.map(lambda x: ('ignored_key', x))

on_time_performance.saveAsNewAPIHadoopFile(
  path='-', 
  outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
  keyClass="org.apache.hadoop.io.NullWritable", 
  valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable", 
  conf={ "es.resource" : "agile_data_science/on_time_performance" })
