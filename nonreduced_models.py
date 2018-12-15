'''
In this file we build models using the fully-featured motif matrix. Testing may be done against balanced test set or not.
'''
from math import sqrt
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib as jb
from assistant_functions import *

np.random.seed(100)

# nonreduced matrix loading

feature_matrix_2 = pd.read_table("feature_matrix_2.csv", sep=",", index_col=0)

feature_matrix_2 = feature_matrix_2.fillna(value=0)

unsplitY = feature_matrix_2.loc[:, '_label']
unsplitX = feature_matrix_2.loc[:, feature_matrix_2.columns.values != '_label']

X_train, X_test, y_train, y_test = train_test_split(unsplitX, unsplitY, test_size=0.33)

feature_number = len(X_train.columns.values)

# model 3 using nonreduced feature dataset_train

classifier3 = RandomForestClassifier(n_jobs=-1, n_estimators=10000, max_features=int(sqrt(feature_number)), max_depth=None,
                                     min_samples_split=2, class_weight='balanced')

classifier3.fit(X_train, y_train)

jb.dump(classifier3, "classifier3.joblib", compress=1)

#classifier3 = jb.load("classifier3.joblib")

predictions3 = classifier3.predict(X_test)

# see how many incorrect classifications we do
crosstab3 = pd.crosstab(y_test, predictions3, rownames=['Actual'], colnames=['Predicted'])
print(crosstab3)
# print a matrix of tuples of feature names and feature importances
classifier3_feature_importances = list(zip(X_train.columns.values, classifier3.feature_importances_))
plt.plot(classifier3.feature_importances_)

probabilities3 = classifier3.predict_proba(X_test)
fpr, tpr, thresholds = roc_curve(y_test, probabilities3[:,1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC3.png')

# model with 1000 trees using non-reduced data

classifierThousand = RandomForestClassifier(n_jobs=-1, n_estimators=1000, max_features=int(sqrt(feature_number)), max_depth=None,
                                            min_samples_split=2, class_weight='balanced')

classifierThousand.fit(X_train, y_train)

jb.dump(classifierThousand, "classifierThousand.joblib", compress=1)

predictions5 = classifierThousand.predict(X_test)
crosstab5 = pd.crosstab(y_test, predictions5, rownames=['Actual'], colnames=['Predicted'])
classifier5_feature_importances = (zip(X_test.columns.values, classifierThousand.feature_importances_))
plt.plot(classifierThousand.feature_importances_)
probabilities5 = classifierThousand.predict_proba(X_test)
fpr, tpr, thresholds = roc_curve(y_test, probabilities5[:, 1], pos_label=1)
ROC_curve(fpr, tpr, 'ROC5.png')

# lets try doing rfc feature reduction

classifier_reduction = RandomForestClassifier(n_jobs=-1, n_estimators=100,
                                              class_weight="balanced")

classifier_reduction.fit(X_train, y_train)

print(confusion_matrix(classifier_reduction, y_test, X_test))

feature_importance_graph(classifier_reduction, X_train.columns.values, 15)

def reduce_n_times(rfc, n, X_train, y_train, X_test, y_test):
    for i in range(0, n):
        best_features = SelectFromModel(rfc, prefit=True)
        X_train = best_features.transform(X_train)
        X_test = best_features.transform(X_test)
        rfc.fit(X_train, y_train)
        print(confusion_matrix(rfc, y_test, X_test))
        ROC_curve_auto(rfc, y_test, X_test, "reducedNTimesAUC.png")
    return rfc, X_train, X_test


five_reduced, X_train_five_reduced, X_test_five_reducd = reduce_n_times(classifier_reduction,
                                                                         5,
                                                                         X_train, y_train,
                                                                         X_test, y_test)

ROC_curve_auto(classifier_reduction, y_test, X_test, "reductionAUC.png")
