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
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold
from scipy import interp
np.random.seed(100)



def ROC_curve(fpr, tpr, savename):
    # by https://qiita.com/bmj0114/items/460424c110a8ce22d945
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, color='orange', label='ROC curve ' % roc_auc)
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

feature_matrix = pd.read_csv("FMs/FM_mast_boruta_reduced.csv").fillna(value=0)
feature_matrix_zeroed = feature_matrix.fillna(value=0)


features = feature_matrix_zeroed.drop(['id','_label'], axis=1).values
y = feature_matrix_zeroed.loc[:,'_label'].values

# 60, 20, 20
#train, validate, test = np.split(feature_matrix_zeroed.sample(frac=1),
#                                 [int(.6*len(feature_matrix_zeroed)), int(.8*len(feature_matrix_zeroed))])


# first probe model

classifier1 = GradientBoostingClassifier(loss='deviance', n_estimators=60)

cv = StratifiedKFold(n_splits=4)
mean_fpr = np.linspace(0,1,100)
tprs = []
aucs = []

i=0
for train,test in cv.split(features,y):
    prediction = classifier1.fit(features[train],y[train]).predict_proba(features[test])
    fpr, tpr, t = roc_curve(y[test], prediction[:, 1])
    tprs.append(interp(mean_fpr, fpr, tpr))
    roc_auc = auc(fpr, tpr)
    aucs.append(roc_auc)
    plt.plot(fpr, tpr, lw=2, alpha=0.3, label='ROC fold %d (AUC = %0.2f)' % (i, roc_auc))
    i= i+1

plt.plot([0,1],[0,1],linestyle = '--',lw = 2,color = 'black')
mean_tpr = np.mean(tprs, axis=0)
mean_auc = auc(mean_fpr, mean_tpr)
plt.plot(mean_fpr, mean_tpr, color='blue', label=r'Mean ROC (AUC = %0.2f )' % (mean_auc),lw=2, alpha=1)
std_auc = np.std(aucs)
std_tpr = np.std(tprs, axis=0)
tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
plt.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2, label=r'$\pm$ 1 std. dev.')
plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.show()
plt.savefig('roc_auc_M.png')
plt.gcf().clear()

exit()