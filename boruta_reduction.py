from __future__ import print_function
import pandas as pd
import joblib as jb
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from boruta import BorutaPy
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

np.random.seed(100)

#references:
#https://www.kaggle.com/tilii7/boruta-feature-elimination/notebook
#https://github.com/scikit-learn-contrib/boruta_py

# Perform feature selection using all-relevant feature selection
# on features that are significant according to MAST

def boruta_runner(n_estimators, X, y):
    # Boruta will die if you give it too many trees (n_estimators) or set it to auto
    # appears to be known and active issue
    # https://github.com/scikit-learn-contrib/boruta_py/issues/16
    rfc1 = RandomForestClassifier(n_jobs=-1, class_weight='balanced')
    boruta_selector = BorutaPy(rfc1, verbose=1, n_estimators=n_estimators)
    boruta_selector.fit(X.as_matrix(), y.as_matrix())
    print('\nSelected %d features out of original set of %d using ensemble of %d trees.'
        % (boruta_selector.n_features_, X.shape[1], boruta_selector.n_estimators))
    return boruta_selector


def multi_boruta(n_estimators_list):
    model_list = []
    for item in n_estimators_list:
        model_list.append(boruta_runner(item, X, y))
    return model_list


def get_selected_feature_names(boruta_selector, X):
    feature_namelist = []
    for i in range(0, X.shape[1]):
        if boruta_selector.support_[i] == True:
            feature_namelist.append(X.columns[i])
    return feature_namelist


def get_reduced_matrix(dataset, feature_namelist, label_name='_label'):
    namelist = [label_name] + feature_namelist
    reduced_matrix = dataset[namelist]
    return reduced_matrix


# Import MAST-reduced training set
dataset_train = pd.read_csv('FMs/FM_mast_reduced_train.csv', index_col=0).fillna(value=0)
X = dataset_train.drop('_label', axis=1)
y = dataset_train['_label']

# With more than 20 trees, we do not do a very good job of
# feature selection. Iterate 5-15 trees.

selection1, selection2, selection3, selection4, selection5 = multi_boruta([5, 10, 15, 20, 25])

# We want around 20 features, so selection5 is probably the best

selection_chosen_feature_names = get_selected_feature_names(selection5, X)

# Get the reduced train set and save to file

train_reduced = get_reduced_matrix(dataset_train, selection_chosen_feature_names)
train_reduced.to_csv('feature_matrix_2_mast_boruta_train_reduced.csv')

# Get the test set, reduce using train info, save

dataset_test = pd.read_csv('FMs/FM_orig_test.csv', index_col=0).fillna(value=0)
test_reduced = get_reduced_matrix(dataset_test, selection_chosen_feature_names)
test_reduced.to_csv('feature_matrix_2_mast_boruta_test_reduced.csv')
