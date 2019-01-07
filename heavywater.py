import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.decomposition import NMF
from collections import Counter
from numpy.linalg import norm
from time import time
from sys import stdout
#from gensim import corpora, models, similarities



heavy_water = pd.read_csv("/Users/jiawang/Documents/heavy/shuffled-full-set-hashed.csv", header=None)
n = len(heavy_water[1])
word_list = []
for i in range(0, n):
    if type(heavy_water[1][i]) != str:
        word_list.append('')
    else:
        word_list.append(heavy_water[1][i].encode('utf-8'))
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(word_list)
Y = X.toarray()
feature_name = vectorizer.get_feature_names()
data = Y
label = heavy_water[0][:]
n = len(label)
train_num = (int)(0.8 * n)
train_data = data[:train_num][:]
train_label = label[:train_num]
test_data = data[train_num:][:]
test_label = label[train_num:]
train_data.shape
print(train_label.shape)
print(test_label.shape)
count = Counter(label)
print(count)
print(len(count))
v = train_data
model = NMF(n_components=14, alpha=0.01)

W = model.fit_transform(v)
H = model.components_
print (W)
print (H)
print(W.dot(H))
print(v)

# lsi = models.LsiModel(v, id2word=dictionary, num_topics=14)
# lsi.print_topics(14)
