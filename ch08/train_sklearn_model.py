import sys, os, re
sys.path.append("lib")
import utils

import numpy as np
import sklearn
import iso8601
import datetime
print("Imports loaded...")

# Load and check the size of our training data. May take a minute.
print("Original JSON file size: {:,} Bytes".format(os.path.getsize("../data/simple_flight_delay_features.jsonl")))
training_data = utils.read_json_lines_file('../data/simple_flight_delay_features.jsonl')
print("Training items: {:,}".format(len(training_data))) # 5,714,008
print("Data loaded...")

# Inspect a record before we alter them
print("Size of training data in RAM: {:,} Bytes".format(sys.getsizeof(training_data))) # 50MB
print(training_data[0])

# # Sample down our training data at first...
# sampled_training_data = training_data#np.random.choice(training_data, 1000000)
# print("Sampled items: {:,} Bytes".format(len(training_data)))
# print("Data sampled...")

# Separate our results from the rest of the data, vectorize and size up
results = [record['ArrDelay'] for record in training_data]
results_vector = np.array(results)
sys.getsizeof(results_vector) # 45,712,160 Bytes
print("Results vectorized...")

# Remove the two delay fields and the flight date from our training data
for item in training_data:
  item.pop('ArrDelay', None)
  item.pop('FlightDate', None)
print("ArrDelay and FlightDate removed from training data...")

# Must convert datetime strings to unix times
for item in training_data:
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
import matplotlib.pyplot as plt

plt.scatter(
  y_test,
  predicted,
  color='blue',
  linewidth=1
)

plt.xticks(())
plt.yticks(())

plt.show()

#
# Swap out LinearRegression for a GradientBoostingRegressor and determing feature importances
#
regressor = GradientBoostingRegressor
print("Swapped gradient boosting trees for linear regression, yet again!")

regressor.fit(X_train, y_train)
print("Gradient boosting regressor fitted...")

predicted = regressor.predict(X_test)
print("Random forest predictions made for X_test...")

# Definitions from http://scikit-learn.org/stable/modules/model_evaluation.html
from sklearn.metrics import median_absolute_error, r2_score
# Median absolute error is the median of all absolute differences between the target and the prediction.
# Less is better, more indicates a high error between target and prediction.
medae = median_absolute_error(y_test, predicted)
print("Gradient boosting regressor median absolute error:    {:.3g}".format(medae))

# R2 score is the coefficient of determination. Ranges from 1-0, 1.0 is best, 0.0 is worst.
# Measures how well future samples are likely to be predicted.
r2 = r2_score(y_test, predicted)
print("Gradient boosting regressor r2 score:                 {:.3g}".format(r2))

#
# Interrogate Model, Visualize Feature Importances
#

# Excellent example here: http://scikit-learn.org/stable/auto_examples/ensemble/plot_forest_importances.html
print(regressor.feature_importances_)

# Print the raw importances... not super useful
importances = regressor.feature_importances_
print(importances)

# Get the feature importances with their labels from DictVectorizer
feature_name_importances = list(zip(vectorizer.get_feature_names(), regressor.feature_importances_))

# Count the feature importances
feature_importance_count = len(feature_name_importances)
print("Total feature importances: {:,}\n".format(feature_importance_count))

# Sort the feature importances in descending order
sorted_feature_importances = sorted(feature_name_importances, key=lambda x: -1 * x[1])

# Print the sorted feature importances
for item in sorted_feature_importances:
    print("{0: <15}: {1}".format(item[0], item[1]))

# Too many! Most are 0. Print only the non-zero feature importances.
non_zero_feature_importances = [feature for feature in sorted_feature_importances if feature[1] > 0.0]
non_zero_count = len(non_zero_feature_importances)
print("Total non-zero feature importances: {}\n".format(non_zero_count))

for item in non_zero_feature_importances:
    print("{0: <15}: {1}".format(item[0], item[1]))

# Plot the top 20 feature importances
top_20_feature_importanes = non_zero_feature_importances[0:20]
top_20_feature_importanes

# Cleans up the appearance
plt.rcdefaults()

labels = [i[0] for i in top_20_feature_importanes]
reversed_labels = list(reversed(labels))

y_pos = [1.6 * item for item in np.arange(len(labels))]

chart_feature_importances = [i[1] for i in top_20_feature_importanes]
reversed_cfis = list(reversed(chart_feature_importances))

# See http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.barh
plt.barh(
  y_pos,
  reversed_cfis,
  align='center',
  alpha=0.5,
  linewidth=0,
)
plt.yticks(y_pos, reversed_labels)
plt.xlabel('Usage')
plt.title('Programming language usage')

plt.show()
