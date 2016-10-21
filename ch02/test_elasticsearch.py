from pyelasticsearch import ElasticSearch
es = ElasticSearch('http://localhost:9200/')
es.search('*', index='agile_data_science')