import cbust_result as cb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_recall_curve, roc_curve, auc
from sklearn.model_selection import train_test_split
from fancyimpute import IterativeImputer
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from boruta import BorutaPy
np.random.seed(100)

feature_matrix = pd.read_table("FMs/FM_mast_boruta_reduced.csv", sep=",", index_col=0)
feature_matrix.head()

feature_matrix_zeroed = feature_matrix.fillna(value=0)


# 60, 20, 20
train, validate, test = np.split(feature_matrix_zeroed.sample(frac=1),
                                 [int(.6*len(feature_matrix_zeroed)), int(.8*len(feature_matrix_zeroed))])

features = train.columns[:-1]
y = train.loc[:,'target']

classifier1 = RandomForestClassifier(n_jobs=2, random_state=0)
classifier1.fit(train[features], y)


predictions = classifier1.predict(test[features])
# see how many incorrect classifications we do
print(pd.crosstab(test['target'], predictions, rownames=['Actual'], colnames=['Predicted']))
precision_recall_curve(test['target'], predictions)
# print a matrix of tuples of feature names and feature importances
list(zip(train[features], classifier1.feature_importances_))
plt.plot( classifier1.feature_importances_)
plt.show()
# get the most important motifs for the random forest
print(features[np.nonzero(classifier1.feature_importances_ > 0.003)])