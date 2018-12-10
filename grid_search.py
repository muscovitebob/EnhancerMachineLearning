import cbust_result as cb
from math import sqrt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import joblib as jb
np.random.seed(100)

# reduced matrix loading

feature_matrix_1 = pd.read_table("FMs/FM_mast_boruta_reduced.csv", sep=",", index_col=0)

feature_matrix_1_zeroed = feature_matrix_1.fillna(value=0)

unsplitY_1 = feature_matrix_1_zeroed.loc[:,'target']
unsplitX_1 = feature_matrix_1_zeroed.loc[:, feature_matrix_1_zeroed.columns.values != 'target']

X_train_1, X_test_1, y_train_1, y_test_1 = train_test_split(unsplitX_1, unsplitY_1, test_size=0.33)

# nonreduced matrix loading


feature_matrix_2 = pd.read_table("feature_matrix_2.csv", sep=",", index_col=0)

feature_matrix_2_zeroed = feature_matrix_2.fillna(value=0)

unsplitY_2 = feature_matrix_2_zeroed.loc[:,'_label']
unsplitX_2 = feature_matrix_2_zeroed.loc[:, feature_matrix_2_zeroed.columns.values != '_label']

X_train_2, X_test_2, y_train_2, y_test_2 = train_test_split(unsplitX_2, unsplitY_2, test_size=0.33)