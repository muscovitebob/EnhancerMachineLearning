import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.metrics import auc, roc_curve


def ROC_curve_auto(rfc, y_test, X_test, savename):
    probabilities = rfc.predict_proba(X_test)
    fpr, tpr, thresholds = roc_curve(y_test, probabilities[:, 1], pos_label=1)
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, color='orange', label='ROC curve %s' % roc_auc)
    plt.plot([0, 1], [0, 1], color='blue', linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic curve')
    plt.legend(loc="lower right")
    plt.savefig(savename)
    plt.show()
    print("AUC: ", roc_auc)


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
    plt.title('Receiver Operating Characteristic curve')
    plt.legend(loc="lower right")
    plt.savefig(savename)
    plt.show()
    print("AUC: ", roc_auc)


def confusion_matrix(rfc, y_test, X_test):
    predictions = rfc.predict(X_test)
    return pd.crosstab(y_test, predictions, rownames=['Actual'], colnames=['Predicted'])


def f(rfc, training_feature_names, n_largest):
    '''
    :param rfc:
    :param training_feature_names: get these using X_train.columns.values
    :param n_largest: how many importances to plot
    :return:
    '''
    shortened_names = [motif.split("/", 1)[0] for motif in training_feature_names]
    named_importances = pd.Series(rfc.feature_importances_, index=shortened_names)
    named_importances.nlargest(n_largest)
    stdev = np.std([tree.feature_importances_ for tree in rfc.estimators_])
    named_importances.plot(kind="barh")
    plt.show()
