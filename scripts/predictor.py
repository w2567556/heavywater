# scripts/predictor.py:
import os,time
from gensim import corpora, models
import numpy as np
import pickle as pkl
from model.model import rf_classify, svm_classify
from scipy.sparse import csr_matrix

def generator_predictor(corpus_lsi, path_tmp_lsi, path_tmp_predictor):
    predictor = None
    train_err_ratio = 0
    train_cm = None
    test_err_ratio = 0
    test_cm = None
    if not os.path.exists(path_tmp_predictor):
        print('=== No predictor in the current folder. Begin generating predictor ===')
        if not corpus_lsi:
            print('--- Lsi files not found ---')
            files = os.listdir(path_tmp_lsi)
            catg_list = []
            for file in files:
                t = file.split('.')[0]
                if t not in catg_list:
                    catg_list.append(t)
            corpus_lsi = {}
            for catg in catg_list:
                path = '{f}{s}{c}.mm'.format(f=path_tmp_lsi,s=os.sep,c=catg)
                corpus = corpora.MmCorpus(path)
                corpus_lsi[catg] = corpus
            print('--- Finish reading lsi file, begin generating predictor ---')

        tag_list = []
        doc_num_list = []
        corpus_lsi_total = []
        catg_list = []
        files = os.listdir(path_tmp_lsi)
        for file in files:
            t = file.split('.')[0]
            if t not in catg_list:
                catg_list.append(t)
        for count,catg in enumerate(catg_list):
            tmp = corpus_lsi[catg]
            tag_list += [count]*tmp.__len__()
            doc_num_list.append(tmp.__len__())
            corpus_lsi_total += tmp
            corpus_lsi.pop(catg)

        data = []
        rows = []
        cols = []
        line_count = 0
        for line in corpus_lsi_total:
            for elem in line:
                rows.append(line_count)
                cols.append(elem[0])
                data.append(elem[1])
            line_count += 1
        lsi_matrix = csr_matrix((data,(rows,cols))).toarray()
        # create test and train data
        rarray=np.random.random(size=line_count)
        train_set = []
        train_tag = []
        test_set = []
        test_tag = []
        for i in range(line_count):
            if rarray[i]<0.8:
                train_set.append(lsi_matrix[i,:])
                train_tag.append(tag_list[i])
            else:
                test_set.append(lsi_matrix[i,:])
                test_tag.append(tag_list[i])

        # generate predictor
        predictor, train_err_ratio, train_cm, test_err_ratio, test_cm  = rf_classify(train_set,train_tag,test_set,test_tag)
        x = open(path_tmp_predictor,'wb')
        pkl.dump(predictor, x)
        x.close()
    else:
        print('=== Predictor detected, skip ===')
    return predictor, train_err_ratio, train_cm, test_err_ratio, test_cm
