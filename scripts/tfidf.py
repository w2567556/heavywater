# scripts/tfidf.py:
import os,time
from gensim import corpora, models
from getData.data import csvStream

def generate_tfidf(dictionary, path_dictionary, path_tmp_tfidf, n):
    corpus_tfidf = None
    if not os.path.exists(path_tmp_tfidf):
        print('=== No tfidf vector in the current folder. Begin generating tfidf vector ===')
        if not dictionary:
            dictionary = corpora.Dictionary.load(path_dictionary)
        os.makedirs(path_tmp_tfidf)
        path_doc_root = './data/shuffled-full-set-hashed.csv'
        files = csvStream(path_doc_root)
        tfidf_model = models.TfidfModel(dictionary=dictionary)
        corpus_tfidf = {}
        for i, (y, x) in enumerate(files):
            if i%n==0:
                catg    = y
                word_list    = x
                file_bow = dictionary.doc2bow(word_list)
                file_tfidf = tfidf_model[file_bow]
                tmp = corpus_tfidf.get(catg,[])
                tmp.append(file_tfidf)
                if tmp.__len__()==1:
                    corpus_tfidf[catg] = tmp
            if i%10000==0:
                print('{i} files is dealed'.format(i=i))
        catgs = list(corpus_tfidf.keys())
        for catg in catgs:
            corpora.MmCorpus.serialize('{f}{s}{c}.mm'.format(f=path_tmp_tfidf,s=os.sep,c=catg),
                                       corpus_tfidf.get(catg),
                                       id2word = dictionary
                                       )
            print('catg {c} has been transformed into tfidf vector'.format(c=catg))
        print('=== Tfidf vector created ===')
    else:
        print('=== Tfidf vector detected, skip ===')
    return corpus_tfidf
