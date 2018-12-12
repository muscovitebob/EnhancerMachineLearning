import matplotlib.pyplot as plt
from sklearn.metrics import auc

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