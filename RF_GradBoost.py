import cbust_result as cb
from math import sqrt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib as jb
from boruta import BorutaPy
np.random.seed(100)
from sklearn.ensemble import GradientBoostingClassifier


def ROC_curve(fpr, tpr, savename):
    # by https://qiita.com/bmj0114/items/460424c110a8ce22d945
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, color='orange', label='ROC curve %s' % roc_auc)
    plt.plot([0, 1], [0, 1], color='blue', linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC')
    plt.legend(loc="lower right")
    plt.savefig(savename)
    plt.show()
    print("AUC: ", roc_auc)

# reduced matrix loading

feature_matrix = pd.read_table("FMs/FM_mast_boruta_reduced.csv", sep=",", index_col=0)

feature_matrix_zeroed = feature_matrix.fillna(value=0)


# 60, 20, 20
train, validate, test = np.split(feature_matrix_zeroed.sample(frac=1),
                                 [int(.6*len(feature_matrix_zeroed)), int(.8*len(feature_matrix_zeroed))])

features = train.columns[:-1]
y = train.loc[:,'target']

# nonreduced matrix loading


feature_matrix_2 = pd.read_table("feature_matrix_2.csv", sep=",", index_col=0)

feature_matrix_2_zeroed = feature_matrix_2.fillna(value=0)


# 60, 20, 20
train_2, validate_2, test_2 = np.split(feature_matrix_2_zeroed.sample(frac=1),
                                 [int(.6*len(feature_matrix_2_zeroed)), int(.8*len(feature_matrix_2_zeroed))])

features_2 = train_2.columns[1:]
y_2 = train_2.loc[:,'_label']

# first probe model

classifier1 = GradientBoostingClassifier(loss='deviance', n_estimators=60)
classifier1.fit(train[features], y)

predictions1 = classifier1.predict(test[features])
# see how many incorrect classifications we do
crosstab1 = pd.crosstab(test['target'], predictions1, rownames=['Actual'], colnames=['Predicted'])
print(crosstab1)
# print a matrix of tuples of feature names and feature importances
list(zip(train[features], classifier1.feature_importances_))
#plt.plot( classifier1.feature_importances_)
#plt.show()
# get the most important motifs for the random forest
#print(features[np.nonzero(classifier1.feature_importances_ > 0.003)])

# model 2 using much bigger tree ensemble

probabilities = classifier1.predict_proba(test.loc[:, test.columns!='target'])
fpr, tpr, thresholds = roc_curve(test['target'], probabilities[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC.png')

exit()











'''
classifier2 = RandomForestClassifier(n_jobs=2, n_estimators=10000, max_features=int(sqrt(len(features))), max_depth=None,
                                     min_samples_split=2)

classifier2.fit(train[features], y)

jb.dump(classifier2, "classifier2.joblib", compress=1)
'''

classifier2 = jb.load('classifier2.joblib')

predictions2 = classifier2.predict(test[features])

# see how many incorrect classifications we do
crosstab2 = pd.crosstab(test['target'], predictions2, rownames=['Actual'], colnames=['Predicted'])
print(crosstab2)
# print a matrix of tuples of feature names and feature importances
featureImportances2 = (zip(train[features], classifier2.feature_importances_))
print(featureImportances2)
plt.plot(classifier2.feature_importances_)
plt.show()

# model 3 using nonreduced feature dataset

'''
classifier3 = RandomForestClassifier(n_jobs=2, n_estimators=10000, max_features=int(sqrt(len(features_2))), max_depth=None,
                                     min_samples_split=2)

classifier3.fit(train_2[features_2], y_2)

jb.dump(classifier3, "classifier3.joblib", compress=1)
'''

classifier3 = jb.load("classifier3.joblib")

predictions3 = classifier3.predict(test_2[features_2])

# see how many incorrect classifications we do
crosstab3 = pd.crosstab(test_2['_label'], predictions3, rownames=['Actual'], colnames=['Predicted'])
print(crosstab3)
# print a matrix of tuples of feature names and feature importances
featureImportances3 = list(zip(train_2[features_2], classifier3.feature_importances_))
print(featureImportances3)
plt.plot(classifier3.feature_importances_)
plt.show()

# model 4 using bigger tree ensemble with reduced data
# does using 10k trees improve over just 1k?

classifier4 = RandomForestClassifier(n_jobs=2, n_estimators=1000, max_features=int(sqrt(len(features))), max_depth=None,
                                     min_samples_split=2)

classifier4.fit(train[features], y)

jb.dump(classifier4, "classifier4.joblib", compress=1)

#classifier4 = jb.load('classifier2.joblib')

predictions4 = classifier4.predict(test[features])

# see how many incorrect classifications we do
crosstab4 = pd.crosstab(test['target'], predictions4, rownames=['Actual'], colnames=['Predicted'])
print(crosstab4)
# print a matrix of tuples of feature names and feature importances
featureImportances4 = (zip(train[features], classifier4.feature_importances_))
print(featureImportances4)
plt.plot(classifier4.feature_importances_)
plt.show()

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

# lets try to do ROC
# compute probabilities for the ROC function
probabilities2 = classifier2.predict_proba(test.loc[:, test.columns!='target'])
fpr, tpr, thresholds = roc_curve(test['target'], probabilities2[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC2.png')


probabilities4 = classifier4.predict_proba(test.loc[:, test.columns!='target'])
fpr, tpr, thresholds = roc_curve(test['target'], probabilities4[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC4.png')

# there really is no difference between 10k and 1k trees.
# carry 1k or less forward from now on

# model 5 using bigger tree ensemble with non-reduced data

classifier5 = RandomForestClassifier(n_jobs=2, n_estimators=1000, max_features=int(sqrt(len(features))), max_depth=None,
                                     min_samples_split=2)

classifier5.fit(train_2[features_2], y_2)
