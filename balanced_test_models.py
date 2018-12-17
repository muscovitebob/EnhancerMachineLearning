'''
In this file we build models and test them using the class balanced dataset, which is also used for
the neural network modelling. We also use class_weight='balanced' to do inverse weighting of the training set.
'''


from math import sqrt
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_curve
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib as jb
from assistant_functions import *

np.random.seed(100)

# Read in the MAST and boruta-reduced training set

train = pd.read_csv('feature_matrix_2_mast_boruta_train_reduced.csv', index_col=0)
X_train = train.loc[:, train.columns.values != '_label']
y_train = train.loc[:, '_label']



test = pd.read_csv('feature_matrix_2_mast_boruta_test_reduced.csv', index_col=0)
X_test = test.loc[:, train.columns.values != '_label']
y_test = test.loc[:, '_label']

classifier1 = RandomForestClassifier(n_jobs=-1, n_estimators=1000, max_depth=None,
                                     min_samples_split=2, class_weight='balanced')

classifier1.fit(X_train, y_train)

jb.dump(classifier1, "classifier1_balanced.joblib", compress=1)

#classifier1 = jb.load("classifier1_balanced.joblib")

predictions1 = classifier1.predict(X_test)

# see how many incorrect classifications we do
confusion_matrix(classifier1, y_test, X_test)

feature_importance_graph(classifier1, X_train.columns.values, 19)



ROC_curve_auto(classifier1, y_test, X_test, 'ROC_final_balanced.png')




'''
# Train the random forest again on the reduced train set to get a model and then predict the test set
forest=RandomForestClassifier(n_jobs=-1,class_weight='balanced',n_estimators=1000)
pred_prob = forest.fit(X_train,y_train).predict_proba(X_test)
fpr, tpr, t = roc_curve(y_test, pred_prob[:,1])
roc_auc = auc(fpr, tpr)
print ("\n Area under ROC curve: %0.3f " % (roc_auc))


# Plot ROC curve without cross validation
plt.plot(fpr, tpr, lw=2, alpha=0.3, label='ROC fold (AUC = %0.3f)' % (roc_auc))
plt.plot([0,1],[0,1],linestyle = '--',lw = 2,color = 'black')
plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.show()
plt.savefig('roc_auc_M.png')
plt.gcf().clear()
'''
