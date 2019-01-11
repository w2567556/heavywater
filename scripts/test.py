# scripts/test.py:
import os,time
from gensim import corpora, models
import pickle as pkl
from scipy.sparse import csr_matrix

#test on new data
def test_new(dictionary, lsi_model, predictor, path_dictionary, path_tmp_lsi, path_tmp_lsimodel, path_tmp_predictor, demo_doc):
    if not dictionary:
        dictionary = corpora.Dictionary.load(path_dictionary)
    if not lsi_model:
        lsi_file = open(path_tmp_lsimodel,'rb')
        lsi_model = pkl.load(lsi_file)
        lsi_file.close()
    if not predictor:
        x = open(path_tmp_predictor,'rb')
        predictor = pkl.load(x)
        x.close()
    files = os.listdir(path_tmp_lsi)
    catg_list = []
    for file in files:
        t = file.split('.')[0]
        if t not in catg_list:
            catg_list.append(t)
    print("Original text:")
    print(demo_doc)
    demo_doc = demo_doc.split(" ")
    demo_bow = dictionary.doc2bow(demo_doc)
    tfidf_model = models.TfidfModel(dictionary=dictionary)
    demo_tfidf = tfidf_model[demo_bow]
    demo_lsi = lsi_model[demo_tfidf]
    data = []
    cols = []
    rows = []
    for item in demo_lsi:
        data.append(item[1])
        cols.append(item[0])
        rows.append(0)
    demo_matrix = csr_matrix((data,(rows,cols))).toarray()
    x = predictor.predict(demo_matrix)
    print('Outcome:{x}'.format(x=catg_list[x[0]]))
    return catg_list[x[0]]
