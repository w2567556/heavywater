# scripts/file.py:
# manage files and paths.
# path_tmp for tmp files
import os

def file_management():
    path_tmp = './tmp/'
    path_dictionary     = os.path.join(path_tmp, 'THUNews.dict')
    path_tmp_tfidf      = os.path.join(path_tmp, 'tfidf_corpus')
    path_tmp_lsi        = os.path.join(path_tmp, 'lsi_corpus')
    path_tmp_lsimodel   = os.path.join(path_tmp, 'lsi_model.pkl')
    path_tmp_predictor  = os.path.join(path_tmp, 'predictor.pkl')

    if not os.path.exists(path_tmp):
        os.makedirs(path_tmp)
    return path_dictionary, path_tmp_tfidf, path_tmp_lsi, path_tmp_lsimodel,path_tmp_predictor
