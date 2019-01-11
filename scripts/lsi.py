# scripts/lsi.py:
import os,time
from gensim import corpora, models
import pickle as pkl

def generate_lsi(dictionary, corpus_tfidf, path_tmp_tfidf, path_tmp_lsi, path_tmp_lsimodel):
    corpus_lsi = None
    lsi_model = None
    if not os.path.exists(path_tmp_lsi):
        print('=== No lsi vector in the current folder. Begin generating lsi vector ===')
        if not dictionary:
            dictionary = corpora.Dictionary.load(path_dictionary)
        if not corpus_tfidf:
            print('--- Tfidf files not found ---')
            files = os.listdir(path_tmp_tfidf)
            catg_list = []
            for file in files:
                t = file.split('.')[0]
                if t not in catg_list:
                    catg_list.append(t)

            corpus_tfidf = {}
            for catg in catg_list:
                path = '{f}{s}{c}.mm'.format(f=path_tmp_tfidf,s=os.sep,c=catg)
                corpus = corpora.MmCorpus(path)
                corpus_tfidf[catg] = corpus
            print('--- Finish reading tfidf, begin generating lsi vector ---')

        # begin building lsi model
        os.makedirs(path_tmp_lsi)
        corpus_tfidf_total = []
        catgs = list(corpus_tfidf.keys())
        for catg in catgs:
            tmp = corpus_tfidf.get(catg)
            corpus_tfidf_total += tmp
        lsi_model = models.LsiModel(corpus = corpus_tfidf_total, id2word=dictionary, num_topics=14)
        # save lsi model
        lsi_file = open(path_tmp_lsimodel,'wb')
        pkl.dump(lsi_model, lsi_file)
        lsi_file.close()
        del corpus_tfidf_total
        print('--- lsi model created ---')

        # generate corpus of lsi, delete corpus of tfidf
        corpus_lsi = {}
        for catg in catgs:
            corpu = [lsi_model[doc] for doc in corpus_tfidf.get(catg)]
            corpus_lsi[catg] = corpu
            corpus_tfidf.pop(catg)
            corpora.MmCorpus.serialize('{f}{s}{c}.mm'.format(f=path_tmp_lsi,s=os.sep,c=catg),
                                       corpu,
                                       id2word=dictionary)
        print('=== Lsi vector created ===')
    else:
        print('=== Lsi vector detected, skip ===')
    return corpus_lsi, lsi_model
