import cbust_result as cb
from math import sqrt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc, accuracy_score
from sklearn.model_selection import train_test_split, GridSearchCV
from pprint import pprint
import numpy as np
import pandas as pd
import joblib as jb
#from random_forests_main import ROC_curve
np.random.seed(100)

# reduced matrix loading

feature_matrix_1 = pd.read_table("feature_matrix_2_mast_boruta_reduced.csv", sep=",", index_col=0)

feature_matrix_1_zeroed = feature_matrix_1.fillna(value=0)

unsplitY_1 = feature_matrix_1_zeroed.loc[:,'_label']
unsplitX_1 = feature_matrix_1_zeroed.loc[:, feature_matrix_1_zeroed.columns.values != '_label']

X_train_1, X_test_1, y_train_1, y_test_1 = train_test_split(unsplitX_1, unsplitY_1, test_size=0.33)

# nonreduced matrix loading

feature_matrix_2 = pd.read_table("feature_matrix_2.csv", sep=",", index_col=0)

feature_matrix_2_zeroed = feature_matrix_2.fillna(value=0)

unsplitY_2 = feature_matrix_2_zeroed.loc[:,'_label']
unsplitX_2 = feature_matrix_2_zeroed.loc[:, feature_matrix_2_zeroed.columns.values != '_label']

X_train_2, X_test_2, y_train_2, y_test_2 = train_test_split(unsplitX_2, unsplitY_2, test_size=0.33)

# what are the parameters used for classifier2?

classifier2 = jb.load('classifier2.joblib')
pprint(classifier2.get_params())
'''
{'bootstrap': True,
 'class_weight': None,
 'criterion': 'gini',
 'max_depth': None,
 'max_features': 5,
 'max_leaf_nodes': None,
 'min_impurity_decrease': 0.0,
 'min_impurity_split': None,
 'min_samples_leaf': 1,
 'min_samples_split': 2,
 'min_weight_fraction_leaf': 0.0,
 'n_estimators': 10000,
 'n_jobs': 2,
 'oob_score': False,
 'random_state': None,
 'verbose': 0,
 'warm_start': False}
 '''

# big model - delete to free up memory

del classifier2

# grid search hyperparameter space


# first I put in some obvious choices to search over, then some others
parameter_space_grid_1 = {'max_features': [5, 10, 15, 20], 'n_estimators': [100, 500, 1000]}
parameter_space_grid_2 = {'max_features': [5, 10, 15], 'n_estimators': [100, 500, 1000]}

gridSearch1 = GridSearchCV(RandomForestClassifier(), param_grid=parameter_space_grid_2, n_jobs=-1,
                           scoring='roc_auc', verbose=2)
gridSearch1.fit(X_train_1, y_train_1)
gridSearch1.best_params_
bestEstimator1 = gridSearch1.best_estimator_
jb.dump(bestEstimator1, 'GridSearchBestEstimator1.joblib', compress=1)
#predictions1 = bestEstimator1.predict()

