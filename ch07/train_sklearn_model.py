import sys, os, re
sys.path.append("lib")
import utils

import numpy as np
import sklearn
import iso8601
import datetime
print("Imports loaded...")

# Load and check the size of our training data. May take a minute.
print("Original JSON file size: {:,} Bytes".format(os.path.getsize("data/simple_flight_delay_features.jsonl")))
#training_data = utils.read_json_lines_file('data/simple_flight_delay_features.jsonl')
training_data = utils.read_json_lines_file('data/simple_flight_sample.jsonl')
print("Training items: {:,}".format(len(training_data))) # 5,714,008
print("Data loaded...")

# Inspect a record before we alter them
print("Size of training data in RAM: {:,} Bytes".format(sys.getsizeof(training_data))) # 50MB
print(training_data[0])

# # Sample down our training data at first...
sampled_training_data = training_data#np.random.choice(training_data, 100000)
print("Sampled items: {:,} Bytes".format(len(training_data)))
print("Data sampled...")

# Separate our results from the rest of the data, vectorize and size up
results = [record['ArrDelay'] for record in sampled_training_data]
results_vector = np.array(results)
sys.getsizeof(results_vector) # 45,712,160 Bytes
print("Results vectorized...")

# Remove the two delay fields and the flight date from our training data
for item in sampled_training_data:
  item.pop('ArrDelay', None)
  item.pop('FlightDate', None)
print("ArrDelay and FlightDate removed from training data...")

# Must convert datetime strings to unix times
for item in sampled_training_data:
  if isinstance(item['CRSArrTime'], str):
    dt = iso8601.parse_date(item['CRSArrTime'])
    unix_time = int(dt.timestamp())
    item['CRSArrTime'] = unix_time
  if isinstance(item['CRSDepTime'], str):
    dt = iso8601.parse_date(item['CRSDepTime'])
    unix_time = int(dt.timestamp())
    item['CRSDepTime'] = unix_time
print("Datetimes converted to unix times...")

# Use DictVectorizer to convert feature dicts to vectors
from sklearn.feature_extraction import DictVectorizer

print("Original dimensions: [{:,}]".format(len(training_data)))
vectorizer = DictVectorizer()
training_vectors = vectorizer.fit_transform(training_data)
print("Size of DictVectorized vectors: {:,} Bytes".format(training_vectors.data.nbytes))
print("Training data vectorized...")

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
  training_vectors,
  results_vector,
  test_size=0.1,
  random_state=43
)
print(X_train.shape, X_test.shape)
print(y_train.shape, y_test.shape)
print("Test train split performed...")

# Train a regressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.metrics import median_absolute_error, r2_score
print("Regressor library and metrics imported...")

regressor = LinearRegression()
print("Regressor instantiated...")

from sklearn.ensemble import GradientBoostingRegressor

regressor = GradientBoostingRegressor
print("Swapped gradient boosting trees for linear regression!")

# Lets go back for now...
regressor = LinearRegression()
print("Swapped back to linear regression!")

regressor.fit(X_train, y_train)
print("Regressor fitted...")

predicted = regressor.predict(X_test)
print("Predictions made for X_test...")

# Definitions from http://scikit-learn.org/stable/modules/model_evaluation.html
from sklearn.metrics import median_absolute_error, r2_score
# Median absolute error is the median of all absolute differences between the target and the prediction.
# Less is better, more indicates a high error between target and prediction.
medae = median_absolute_error(y_test, predicted)
print("Median absolute error:    {:.3g}".format(medae))

# R2 score is the coefficient of determination. Ranges from 1-0, 1.0 is best, 0.0 is worst.
# Measures how well future samples are likely to be predicted.
r2 = r2_score(y_test, predicted)
print("r2 score:                 {:.3g}".format(r2))

# Plot outputs, compare actual vs predicted values
# import matplotlib.pyplot as plt
#
# plt.scatter(
#   y_test,
#   predicted,
#   color='blue',
#   linewidth=1
# )
#
# plt.xticks(())
# plt.yticks(())
#
# plt.show()

#
# Persist model using pickle
#
print("Testing model persistance...")

import pickle

project_home = os.environ["PROJECT_HOME"]

# Dump the model itself
regressor_path = "{}/models/sklearn_regressor.pkl".format(project_home)

regressor_bytes = pickle.dumps(regressor)
model_f = open(regressor_path, 'wb')
model_f.write(regressor_bytes)

# Dump the DictVectorizer that vectorizes the features
vectorizer_path = "{}/models/sklearn_vectorizer.pkl".format(project_home)

vectorizer_bytes = pickle.dumps(vectorizer)
vectorizer_f = open(vectorizer_path, 'wb')
vectorizer_f.write(vectorizer_bytes)

# Load the model itself
model_f = open(regressor_path, 'rb')
model_bytes = model_f.read()
regressor = pickle.loads(model_bytes)

# Load the DictVectorizer
vectorizer_f = open(vectorizer_path, 'rb')
vectorizer_bytes = vectorizer_f.read()
vectorizer = pickle.loads(vectorizer_bytes)

#
# Persist model using sklearn.externals.joblib
#
from sklearn.externals import joblib

# Dump the model and vectorizer
joblib.dump(regressor, regressor_path)
joblib.dump(vectorizer, vectorizer_path)

# Load the model and vectorizer
regressor = joblib.load(regressor_path)
vectorizer = joblib.load(vectorizer_path)
