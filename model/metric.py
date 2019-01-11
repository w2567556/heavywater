from sklearn.metrics import confusion_matrix as cm
import numpy as np
import json, base64
# calculating metrics
def checkPred(data_tag, data_pred):
    if data_tag.__len__() != data_pred.__len__():
        raise RuntimeError('The length of data tag and data pred should be the same')
    err_count = 0
    for i in range(data_tag.__len__()):
        if data_tag[i]!=data_pred[i]:
            err_count += 1
    err_ratio = float(err_count)/ data_tag.__len__()
    return [err_ratio, cm(data_tag, data_pred).tolist()]
