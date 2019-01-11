import numpy as np
import pandas as pd
from sklearn import datasets
from metric import checkPred
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV


# SVM model for ML
def rf_classify(train_set,train_tag,test_set,test_tag):
    #random select parameters
    # n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
    # max_features = ['auto', 'sqrt']
    # max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
    # max_depth.append(None)
    # min_samples_split = [2, 5, 10]
    # min_samples_leaf = [1, 2, 4]
    # bootstrap = [True, False]
    # random_grid = {'n_estimators': n_estimators,
    #                'max_features': max_features,
    #                'max_depth': max_depth,
    #                'min_samples_split': min_samples_split,
    #                'min_samples_leaf': min_samples_leaf,
    #                'bootstrap': bootstrap}
    #
    # param_grid = {"bootstrap": [False],
    #               "max_features": ['auto'],
    #               "n_estimators" : [1500, 1600, 1700],
    #               "max_depth" : [25, 30, 35],
    #               "min_samples_split": [2, 5, 7],
    #               "min_samples_leaf": [0.5, 1, 2]}
    clf =  RandomForestClassifier(bootstrap=false, max_features='auto', n_estimators=1500, max_depth=30, min_samples_split=5, min_samples_leaf=1)
    #rfc = RandomForestClassifier()
    #clf = RandomizedSearchCV(rfc, random_grid, n_jobs=-1, cv=5)
    #clf = GridSearchCV(rfc, param_grid, n_jobs=-1, cv=5)
    clf_res = clf.fit(train_set,train_tag)
    #print(clf.best_params_)
    train_pred  = clf_res.predict(train_set)
    test_pred = clf_res.predict(test_set)
    train_err_ratio, train_cm = checkPred(train_tag, train_pred)
    test_err_ratio, test_cm  = checkPred(test_tag, test_pred)

    print('=== Finish training models, please check error rate and confusion matrix===')
    print('train error: {0:.3f}'.format(train_err_ratio))
    print('confusion matrix for training  {e}'.format(e=train_cm))
    print('test error: {0:.3f}'.format(test_err_ratio))
    print('confusion matrix for testing  {e}'.format(e=test_cm))
    return clf_res,  train_err_ratio, train_cm, test_err_ratio, test_cm

# SVM model for ML
def svm_classify(train_set,train_tag,test_set,test_tag):
    clf = svm.LinearSVC()
    clf_res = clf.fit(train_set,train_tag)
    train_pred  = clf_res.predict(train_set)
    test_pred = clf_res.predict(test_set)
    train_err_num, train_err_ratio = checkPred(train_tag, train_pred)
    test_err_num, test_err_ratio  = checkPred(test_tag, test_pred)

    print('=== Finish training models, please check error rate ===')
    print('train error: {0:.3f}'.format(e=train_err_ratio))
    print('test error: {0:.3f}'.format(e=test_err_ratio))

    return clf_res, train_err_ratio, train_cm, test_err_ratio, test_cm
