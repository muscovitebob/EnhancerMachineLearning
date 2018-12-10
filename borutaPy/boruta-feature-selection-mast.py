#references:
#https://www.kaggle.com/tilii7/boruta-feature-elimination/notebook
#https://github.com/scikit-learn-contrib/boruta_py
#https://www.kaggle.com/kanncaa1/roc-curve-with-k-fold-cv

#Boruta feature selection:
from __future__ import print_function
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from boruta import BorutaPy
from scipy import interp
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import StratifiedKFold

ftrm= pd.read_csv('feature_matrix_2_mast_reduced.csv').fillna(value=0)
ftrm_id = ftrm['id'].values
X = ftrm.drop(['id','X_label'], axis=1).values
y = ftrm['X_label'].values

rfc=RandomForestClassifier(n_jobs=-1,class_weight='balanced')
boruta_selector = BorutaPy(rfc, n_estimators='auto', verbose=2)
boruta_selector.fit(X, y)
# number of selected features
print ('\n Number of selected features:')
print (boruta_selector.n_features_)

feature_df = pd.DataFrame(ftrm.drop(['id','X_label'], axis=1).columns.tolist(), columns=['features'])
feature_df['rank']=boruta_selector.ranking_
feature_df = feature_df.sort_values('rank', ascending=True).reset_index(drop=True)
print ('\n Top %d features:' % boruta_selector.n_features_)
print (feature_df.head(boruta_selector.n_features_))
feature_df.to_csv('boruta-feature-ranking-mast.csv', index=False)

selected = ftrm.drop(['id','X_label'], axis=1).columns[boruta_selector.support_]
ftrm = ftrm[selected]
ftrm['id'] = ftrm_id
ftrm['X_label'] = y
ftrm = ftrm.set_index('id')
ftrm.to_csv('boruta_filtered-matrix.csv', index_label='id')

#Receiver Operating Characteristic (ROC) with cross validation:

data = pd.read_csv('boruta_filtered-matrix.csv').fillna(value=0)
X = data.drop(['id','X_label'], axis=1).values
y = data['X_label'].values
forest=RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=5)
cv = StratifiedKFold(n_splits=10,shuffle=False)
tprs = []
aucs = []
mean_fpr = np.linspace(0,1,100)
i = 1

for train,test in cv.split(X,y):
    prediction = forest.fit(X[train],y[train]).predict_proba(X[test])
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
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()
plt.savefig('roc_auc_M.png')
plt.gcf().clear()
