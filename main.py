
from scripts.dictionary import generate_dictionary
from scripts.lsi import generate_lsi
from scripts.predictor import generator_predictor
from scripts.tfidf import generate_tfidf
from scripts.test import test_new
from scripts.file import file_management
from scripts.delete import delete_tmp
import os, time


def train_model():
    path_dictionary, path_tmp_tfidf, path_tmp_lsi, path_tmp_lsimodel,path_tmp_predictor = file_management()
    sample_rate = 1
    start_time = time.time()
    dictionary = generate_dictionary(path_dictionary, sample_rate)
    corpus_tfidf = generate_tfidf(dictionary, path_dictionary, path_tmp_tfidf, sample_rate)
    corpus_lsi, lsi_model = generate_lsi(dictionary, corpus_tfidf, path_dictionary, path_tmp_tfidf, path_tmp_lsi, path_tmp_lsimodel)
    predictor, train_err_ratio, train_cm, test_err_ratio, test_cm = generator_predictor(corpus_lsi, path_tmp_lsi, path_tmp_predictor)
    end_train_time  = time.time()
    consume_time = end_train_time-start_time
    print('Time consuming for training model and test given data:{x}s'.format(x=consume_time))
    return dictionary, lsi_model, predictor, train_err_ratio, train_cm, test_err_ratio, test_cm, consume_time

def test_model(dictionary, lsi_model, predictor, demo_doc):

    path_dictionary, path_tmp_tfidf, path_tmp_lsi, path_tmp_lsimodel,path_tmp_predictor = file_management()
    start_time = time.time()
    result = test_new(dictionary, lsi_model, predictor, path_dictionary, path_tmp_lsi, path_tmp_lsimodel, path_tmp_predictor, demo_doc)
    end_test_time = time.time()
    consume_time = end_test_time-start_time
    print('Time consuming for training model:{x}s'.format(x=consume_time))
    return result, consume_time


if __name__ == '__main__':

    demo_doc = """
    b44297cf911c 84884d80641d bad6ff5dd7bc bad6ff5dd7bc
    """
    delete_tmp()
    dictionary, lsi_model, predictor, train_err_ratio, train_cm, test_err_ratio, test_cm, consume_time = train_model()
    result, consume_time = test_model(dictionary, lsi_model, predictor, demo_doc)
