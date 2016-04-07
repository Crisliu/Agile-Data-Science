# Load the on-time parquet file
on_time_dataframe = sqlContext.read.parquet('../data/on_time_performance.parquet')

wikidata = sqlContext.read.json('../data/wikidata-20160404-all.json.bz2')
