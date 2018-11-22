import cbust_result as cb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

np.random.seed(100)
feature_matrix = pd.read_table("feature_matrix.csv", sep=",", index_col=0)
feature_matrix.head()

train, validate, test = np.split(feature_matrix.sample(frac=1),
                                 [int(.6*len(feature_matrix)), int(.8*len(feature_matrix))])