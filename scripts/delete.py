# scripts/delete.py:
import os
from scripts.file import file_management

def delete_tmp():
    path_dictionary, path_tmp_tfidf, path_tmp_lsi, path_tmp_lsimodel, path_tmp_predictor = file_management()
    # if os.path.exists(path_dictionary):
    #     os.remove(path_dictionary)
    #     print("Dictionary has been deleted")
    # else:
    #     print("Can't find Dictionary")
    # if os.path.exists(path_tmp_tfidf):
    #     for dirpath, dirnames, filenames in os.walk(path_tmp_tfidf):
    #         for filepath in filenames:
    #             os.remove(os.path.join(path_tmp_tfidf, filepath))
    #     os.removedirs(path_tmp_tfidf)
    #     print("tfidf vector has been deleted")
    # else:
    #     print("Can't find tfidf vector")
    # if os.path.exists(path_tmp_lsi):
    #     for dirpath, dirnames, filenames in os.walk(path_tmp_lsi):
    #         for filepath in filenames:
    #             os.remove(os.path.join(path_tmp_lsi, filepath))
    #     os.removedirs(path_tmp_lsi)
    #     print("lsi vector has been deleted")
    # else:
    #     print("Can't find lsi vector")
    # if os.path.exists(path_tmp_lsimodel):
    #     os.remove(path_tmp_lsimodel)
    #     print("lsimodel has been deleted")
    # else:
    #     print("Can't find lsimodel")
    if os.path.exists(path_tmp_predictor):
        os.remove(path_tmp_predictor)
        print("Predictor has been deleted")
    else:
        print("Can't find Predictor")
