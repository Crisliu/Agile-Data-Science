import sys, os, re
sys.path.append("lib")
import utils

import numpy as np
import sklearn

# Load and check the size of our training data. May take a minute.
training_data = utils.read_json_lines_file('data/simple_flight_delay_features.jsonl')
len(training_data) # 5,714,008

# Separate our results from the rest of the data, vectorize and size up
results = [record['DepDelayMinutes'] for record in training_data]
results_vector = np.array(results)
sys.getsizeof(results_vector) # 45,712,160 bytes

# Remove the two delay fields and the flight date from our training data
for item in training_data:
  del item['DepDelayMinutes']
  del item['ArrDelayMinutes']
  del item['FlightDate']

# Use DictVectorizer to convert feature dicts to vectors
from sklearn.feature_extraction import DictVectorizer

vectorizer = DictVectorizer()
training_vectors = vectorizer.fit_transform(training_data)
training_vectors.data.nbytes # 182,848,256

# Train a gradient boosted regressor
from sklearn.ensemble import GradientBoostingRegressor

regressor = GradientBoostingRegressor()
regressor.fit(training_vectors, results_vector)  # make sure you int() on the number string results

# Get the accuracy through cross validation
scores = sklearn.cross_validation.cross_val_score(regressor, training_vectors.toarray(), results_vector, cv=5)

