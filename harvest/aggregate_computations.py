import json
from datetime import datetime
from dateutil import relativedelta as rd
import unittest
from collections import OrderedDict
import harvest.category_labels as catgory_labels
import harvest.transactions_processor as tp
import scipy
import harvest.maths as maths
import harvest
from tabulate import tabulate
from collections import defaultdict
import re
import dedupe
import os
import pandas as pd



class TestAggregateComputations(unittest.TestCase):


    def setUp(self):
        self.transactions = pd.read_json('data/aggregate-transactions.json', 
                                         lines = True, 
                                         keep_default_dates = False,
                                         dtype = {
                                             'category_id': 'str'
                                            }
                                         )
        self.hc = harvest.category_labels.loadLabeled()

    def testAggregateComputations(self):
        data = tp.processing_pipeline(self.transactions, self.hc)
        median_amount = data.groupby('harvest_category')['amount'].median()
        print(median_amount)
        # monthly etc - you used to spend ... every month but haven't done it this month
            # payment is coming up in x days
        # abnormal spends

    def testDedupe(self):
        settings_file = 'deduper_learned_settings'
        training_file = 'deduper_training.json'

        fields = [
            {'field' : 'name', 'type': 'String'},
        ]

        data = {}
        with open('data/aggregate-transactions.json', 'r') as f:
            for line in f:
                row = json.loads(line)
                data[row['transaction_id']] = row

        """
        if os.path.exists(settings_file):
            print('reading from', settings_file)
            with open(settings_file, 'rb') as f:
                deduper = dedupe.StaticDedupe(f)
        else: 
            deduper = dedupe.Dedupe(fields)
            deduper.sample(data, 15000)

            if os.path.exists(training_file):
                print('reading labeled examples from ', training_file)
                with open(training_file, 'rb') as f:
                    deduper.readTraining(f)

            print('starting active labeling...')

            dedupe.consoleLabel(deduper)
            deduper.train()

            with open(training_file, 'w') as tf:
                deduper.writeTraining(tf)

            with open(settings_file, 'wb') as sf:
                deduper.writeSettings(sf)

        threshold = deduper.threshold(data, recall_weight=1)

        print('clustering...')
        clustered_dupes = deduper.match(data, threshold)

        print('# duplicate sets', len(clustered_dupes))

        cluster_membership = {}
        cluster_id = 0
        for (cluster_id, cluster) in enumerate(clustered_dupes):
            id_set, scores = cluster
            cluster_d = [data[c] for c in id_set]
            print('culster')
            d = [i['name'] for i in cluster_d]
            print(d)
    """




if __name__ == "__main__":
    unittest.main()
