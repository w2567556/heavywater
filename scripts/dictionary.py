# scripts/dictionary.py:
import os,time
from getData.data import csvStream
from gensim import corpora, models

def generate_dictionary(path_dictionary, n):
    dictionary = None
    if not os.path.exists(path_dictionary):
        print('No dictionary in the current folder. Begin generating dictionary')
        dictionary = corpora.Dictionary()
        path_doc_root = './data/shuffled-full-set-hashed.csv'
        files = csvStream(path_doc_root)
        for i,(y,x) in enumerate(files):
            if i%n==0:
                catg = y
                feature = x
                dictionary.add_documents([feature])
                if int(i/n)%10000==0:
                    print('{t} *** {i} \t docs has been dealed'
                          .format(i=i,t=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())))

        #small_freq_ids = [tokenid for tokenid, docfreq in dictionary.dfs.items() if docfreq < 5 ]
         # delete the least frequent items
        #dictionary.filter_tokens(small_freq_ids)
        dictionary.compactify()
        dictionary.save(path_dictionary)
        print('=== Directionary has been created ===')
    else:
        print('=== Directionary detected, skip ===')
    return dictionary
