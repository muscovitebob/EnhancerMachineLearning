from __future__ import print_function
import pandas as pd
import joblib as jb
from sklearn.ensemble import RandomForestClassifier
from boruta import BorutaPy
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

#references:
#https://www.kaggle.com/tilii7/boruta-feature-elimination/notebook
#https://github.com/scikit-learn-contrib/boruta_py
#https://www.kaggle.com/kanncaa1/roc-curve-with-k-fold-cv

# Perform feature selection using all-relevant feature selection
# on features that are significant according to MAST

# Import MAST-reduced training set
ftrm = pd.read_csv('FMs/FM_mast_reduced_train.csv').fillna(value=0)
ftrm_id = ftrm['id']
X = ftrm.drop(['id','_label'], axis=1)
y = ftrm['_label']

def boruta_runner(n_estimators, X, y):
    rfc1 = RandomForestClassifier(n_jobs=-1, class_weight='balanced')
    boruta_selector = BorutaPy(rfc1, verbose=2, n_estimators=n_estimators)
    boruta_selector.fit(X.as_matrix(), y.as_matrix())
    print('\nSelected %d features out of original set of %d using ensemble of %d trees.'
        % (boruta_selector.n_features_, X.shape[1], boruta_selector.n_estimators))
    return boruta_selector

# Boruta will die if you give it too many trees (n_estimators) or set it to auto
# appears to be known and active issue
# https://github.com/scikit-learn-contrib/boruta_py/issues/16
# Additionally, with more than 20 trees, we do not do a very good job of
# feature selection. Iterate 5-15 trees.

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



selection1, selection2, selection3, selection4 = multi_boruta([5, 8, 10, 15])

# We want around 20 features, so selection2 is probably the best

selection2_chosen_feature_names = get_selected_feature_names(selection2)

feature_df = pd.DataFrame(ftrm.drop(['id','_label'], axis=1).columns.tolist(), columns=['features'])
feature_df['rank'] = boruta_selector.ranking_
feature_df = feature_df.sort_values('rank', ascending=True).reset_index(drop=True)
print('\n Top %d features:' % boruta_selector.n_features_)
print (feature_df.head(boruta_selector.n_features_))
feature_df.to_csv('boruta-feature_ranking-mast.csv', index=False)

# Get the reduced train set
ftrm= pd.read_csv('FM_mast_reduced_train.csv').fillna(value=0)
selected = ftrm.drop(['id','_label'], axis=1).columns[boruta_selector.support_]
ftrm = ftrm[selected]
ftrm['id'] = ftrm_id
ftrm['_label'] = y
ftrm = ftrm.set_index('id')
train_reduced=ftrm
train_reduced.to_csv('feature_matrix_2_mast_boruta_train_reduced.csv', index_label='id')
train = pd.read_csv('feature_matrix_2_mast_boruta_train_reduced.csv').fillna(value=0)
X_train = train.drop(['id','_label'], axis=1).values
y_train = train['_label']


# Get the reduced test set
test = pd.read_csv('FM_orig.csv').fillna(value=0)
X_test = test[selected]
y_test = test['_label'].values

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
