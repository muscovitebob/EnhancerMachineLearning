from math import sqrt
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_curve
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib as jb
from assistant_functions import ROC_curve

np.random.seed(100)

# reduced matrix loading

feature_matrix_1 = pd.read_table("feature_matrix_2_mast_boruta_reduced.csv", sep=",", index_col=0)

feature_matrix_1_zeroed = feature_matrix_1.fillna(value=0)

unsplitY_1 = feature_matrix_1_zeroed.loc[:,'_label']
unsplitX_1 = feature_matrix_1_zeroed.loc[:, feature_matrix_1_zeroed.columns.values != '_label']

X_train_1, X_test_1, y_train_1, y_test_1 = train_test_split(unsplitX_1, unsplitY_1, test_size=0.33)

features_1 = len(X_train_1.columns.values)

# nonreduced matrix loading

feature_matrix_2 = pd.read_table("feature_matrix_2.csv", sep=",", index_col=0)

feature_matrix_2_zeroed = feature_matrix_2.fillna(value=0)

unsplitY_2 = feature_matrix_2_zeroed.loc[:,'_label']
unsplitX_2 = feature_matrix_2_zeroed.loc[:, feature_matrix_2_zeroed.columns.values != '_label']

X_train_2, X_test_2, y_train_2, y_test_2 = train_test_split(unsplitX_2, unsplitY_2, test_size=0.33)

features_2 = len(X_train_2.columns.values)

# first probe using gradient boosting model

classifier1 = GradientBoostingClassifier(loss='deviance', n_estimators=60)
classifier1.fit(X_train_1, y_train_1)

predictions1 = classifier1.predict(X_test_1)

probabilities1 = classifier1.predict_proba(X_test_1)
fpr, tpr, thresholds = roc_curve(y_test_1, probabilities1[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC2.png')
# see how many incorrect classifications we do
crosstab1 = pd.crosstab(y_test_1, predictions1, rownames=['Actual'], colnames=['Predicted'])
print(crosstab1)
# print a matrix of tuples of feature names and feature importances
classifier1_feature_importances = list(zip(X_train_1.columns.values, classifier1.feature_importances_))
plt.plot(classifier1.feature_importances_)
#plt.show()
# get the most important motifs for the random forest
#print(features[np.nonzero(classifier1.feature_importances_ > 0.003)])

probabilities1 = classifier1.predict_proba(X_test_1)
fpr, tpr, thresholds = roc_curve(y_test_1, probabilities1[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROCgradboost1.png')

# model 2 using much bigger tree ensemble

classifier2 = RandomForestClassifier(n_jobs=2, n_estimators=10000, max_features=int(sqrt(features_1)), max_depth=None,
                                     min_samples_split=2, class_weight='balance')

classifier2.fit(X_train_1, y_test_1)

jb.dump(classifier2, "classifier2.joblib", compress=1)

#classifier2 = jb.load('classifier2.joblib')

predictions2 = classifier2.predict(X_test_1)

# see how many incorrect classifications we do
crosstab2 = pd.crosstab(y_test_1, predictions2, rownames=['Actual'], colnames=['Predicted'])
print(crosstab2)
# print a matrix of tuples of feature names and feature importances
classifier2_feature_importances = list(zip(X_train_1.columns.values, classifier2.feature_importances_))
print(classifier2_feature_importances)
plt.plot(classifier2.feature_importances_)

# lets try to do ROC
# compute probabilities for the ROC function
probabilities2 = classifier2.predict_proba(X_test_1)
fpr, tpr, thresholds = roc_curve(y_test_1, probabilities2[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC2.png')

# model 3 using nonreduced feature dataset

classifier3 = RandomForestClassifier(n_jobs=2, n_estimators=10000, max_features=int(sqrt(features_2)), max_depth=None,
                                     min_samples_split=2, class_weight='balanced')

classifier3.fit(X_train_2, y_train_2)

jb.dump(classifier3, "classifier3.joblib", compress=1)

#classifier3 = jb.load("classifier3.joblib")

predictions3 = classifier3.predict(X_test_2)

# see how many incorrect classifications we do
crosstab3 = pd.crosstab(y_test_2, predictions3, rownames=['Actual'], colnames=['Predicted'])
print(crosstab3)
# print a matrix of tuples of feature names and feature importances
classifier3_feature_importances = list(zip(X_train_2.columns.values, classifier3.feature_importances_))
plt.plot(classifier3.feature_importances_)

probabilities3 = classifier3.predict_proba(X_test_2)
fpr, tpr, thresholds = roc_curve(y_test_1, probabilities3[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC3.png')

# model 4 using bigger tree ensemble with reduced data
# does using 10k trees improve over just 1k?

classifier4 = RandomForestClassifier(n_jobs=2, n_estimators=1000, max_features=int(sqrt(features_1)), max_depth=None,
                                     min_samples_split=2, class_weight='balanced')

classifier4.fit(X_train_1, y_train_1)

jb.dump(classifier4, "classifier4.joblib", compress=1)

#classifier4 = jb.load('classifier2.joblib')

predictions4 = classifier4.predict(X_test_1)

# see how many incorrect classifications we do
crosstab4 = pd.crosstab(y_test_1, predictions4, rownames=['Actual'], colnames=['Predicted'])
print(crosstab4)
# print a matrix of tuples of feature names and feature importances
classifier4_feature_importances = (zip(X_test_1.columns.values, classifier4.feature_importances_))
plt.plot(classifier4.feature_importances_)

# so is it better?

crosstab2

'''Predicted     0    1
Actual              
0          2471  209
1          1065  274'''

crosstab4

'''Predicted     0    1
Actual              
0          2468  212
1          1068  271'''

# not particularly, no. but need better way to classify performance


probabilities4 = classifier4.predict_proba(X_test_1)
fpr, tpr, thresholds = roc_curve(y_test_1, probabilities4[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC4.png')

# there really is no difference between 10k and 1k trees.
# carry 1k or less forward from now on

# model 5 using bigger tree ensemble with non-reduced data

classifier5 = RandomForestClassifier(n_jobs=2, n_estimators=1000, max_features=int(sqrt(features_2)), max_depth=None,
                                     min_samples_split=2, class_weight='balanced')

classifier5.fit(X_train_2, y_train_2)

jb.dump(classifier5, "classifier5.joblib", compress=1)

predictions5 = classifier5.predict(X_test_2)
crosstab5 = pd.crosstab(y_test_2, predictions5, rownames=['Actual'], colnames=['Predicted'])
classifier5_feature_importances = (zip(X_test_2.columns.values, classifier5.feature_importances_))
plt.plot(classifier5.feature_importances_)
probabilities5 = classifier5.predict_proba(X_test_2)
fpr, tpr, thresholds = roc_curve(y_test_2, probabilities5[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC5.png')