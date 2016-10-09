import sys, os, re
sys.path.append("lib")
import utils

import numpy as np
import sklearn

# Load and check the size of our training data. May take a minute.
training_data = utils.read_json_lines_file('data/simple_flight_delay_features.jsonl')
len(training_data) # 5,714,008
print("Data loaded...")

# Inspect a record before we alter them
print(training_data[0])

# Sample down our training data at first...
sampled_training_data = np.random.choice(training_data, 100000)
print("Data sampled...")

# Separate our results from the rest of the data, vectorize and size up
results = [record['DepDelay'] for record in sampled_training_data]
results_vector = np.array(results)
sys.getsizeof(results_vector) # 45,712,160 bytes
print("Results vectorized...")

# Remove the two delay fields and the flight date from our training data
for item in sampled_training_data:
  item.pop('DepDelay', None)
  item.pop('ArrDelay', None)
  item.pop('FlightDate', None)

# Use DictVectorizer to convert feature dicts to vectors
from sklearn.feature_extraction import DictVectorizer

vectorizer = DictVectorizer()
training_vectors = vectorizer.fit_transform(sampled_training_data)
training_vectors.data.nbytes # 182,848,256
print("Training data vectorized...")

# Train a gradient boosted regressor
from sklearn.linear_model import LinearRegression

regressor = LinearRegression()
regressor.fit(training_vectors, results_vector)  # make sure you int() on the number string results
print("Regression fit...")

# # Get the accuracy through cross validation
# scores = sklearn.model_selection.cross_val_score(
#   regressor,
#   training_vectors.toarray(),
#   results_vector,
#   cv=10
# )
# print scores.mean() # 0.00103472777306

# Try that again, with our own splits
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.metrics import explained_variance_score, mean_absolute_error, median_absolute_error, r2_score

X_train, X_test, y_train, y_test = train_test_split(
  training_vectors.toarray(),
  results_vector,
  test_size=0.1,
  random_state=43
)
regressor.fit(X_train, y_train)
predicted = regressor.predict(X_test)

# Definitions from http://scikit-learn.org/stable/modules/model_evaluation.html

# Median absolute error is the median of all absolute differences between the target and the prediction.
# Less is better, more indicates a high error between target and prediction.
medae = median_absolute_error(y_test, predicted)
print("Median absolute error:    {:.3g}".format(medae))

# R2 score is the coefficient of determination. Ranges from 1-0, 1.0 is best, 0.0 is worst.
# Measures how well future samples are likely to be predicted.
r2 = r2_score(y_test, predicted)
print("r2 score:                 {:.3g}".format(r2))

# Plot outputs
import matplotlib.pyplot as plt

#plt.scatter(X_test, y_test,  color='black')
plt.scatter(
  y_test,
  predicted,
  color='blue',
  linewidth=1
)

plt.xticks(())
plt.yticks(())

plt.show()
