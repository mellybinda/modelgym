import numpy as np
#from cat_counter import CatCounter
from modelgym.model import TASK_CLASSIFICATION, TASK_REGRESSION
from sklearn.model_selection import StratifiedKFold, KFold, train_test_split
from collections import namedtuple

XYCDataset = namedtuple('XYCDataset', ['X', 'y', 'cat_cols'])


def preprocess_cat_cols(X_train, y_train, cat_cols, X_test=None, cc=None, 
                        counters_sort_col=None, learning_task=TASK_CLASSIFICATION):
    pass
#    if cc is None:
#        sort_values = None if counters_sort_col is None else X_train[:, counters_sort_col]
#        cc = CatCounter(learning_task, sort_values)
#        X_train[:,cat_cols] = cc.fit(X_train[:,cat_cols], y_train)
#    else:
#        X_train[:,cat_cols] = cc.transform(X_train[:,cat_cols])
#    if not X_test is None:
#        X_test[:,cat_cols] = cc.transform(X_test[:,cat_cols])
#    return cc


def elementwise_loss(y, p, learning_task=TASK_CLASSIFICATION):
    if learning_task == TASK_CLASSIFICATION:
        p_ = np.clip(p, 1e-16, 1-1e-16)
        return - y * np.log(p_) - (1 - y) * np.log(1 - p_)
    return (y - p) ** 2


def split_and_preprocess(X_train, y_train, X_test, y_test, cat_cols=[], n_splits=5, random_state=0, holdout_size=0, learning_task=TASK_CLASSIFICATION):
    if holdout_size > 0:
        print('Holdout is used for counters.')
        X_train, X_hout, y_train, y_hout = train_test_split(X_train, y_train, 
                                                            test_size=holdout_size,
                                                            random_state=random_state)
        cc = preprocess_cat_cols(X_hout, y_hout, cat_cols)
    else:
        cc = None

    CVSplit = KFold if learning_task == TASK_REGRESSION else StratifiedKFold
    cv = CVSplit(n_splits=n_splits, shuffle=True, random_state=random_state)

    cv_pairs = []
    for train_index, test_index in cv.split(X_train, y_train):
        fold_X_train = X_train[train_index]
        fold_X_test = X_train[test_index]
        fold_y_train = y_train[train_index]
        fold_y_test = y_train[test_index]
        preprocess_cat_cols(fold_X_train, fold_y_train, cat_cols, fold_X_test, cc)
        dtrain = XYCDataset(fold_X_train.astype(float), fold_y_train, cat_cols)
        dtest = XYCDataset(fold_X_test.astype(float), fold_y_test, cat_cols)
        cv_pairs.append((dtrain, dtest))

    _ = preprocess_cat_cols(X_train, y_train, cat_cols, X_test, cc)
    full_dtrain = XYCDataset(X_train.astype(float), y_train, cat_cols)
    full_dtest = XYCDataset(X_test.astype(float), y_test, cat_cols)

    return cv_pairs, (full_dtrain, full_dtest)


