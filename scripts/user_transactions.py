import pandas as pd
import json
from pandas.io.json import json_normalize
from harvest import category_labels
from harvest import transactions_processor as tp
import pdb
import numpy as np


def load(file):
    hc = category_labels.loadLabeled()
    with open(file) as f:
        for line in f:
            dp = json.loads(line)
            if dp:
                val = tp.process(dp['transactions-raw'], hc, tp.request_options({'daterange': 'all'}))
                yield val

def assign_labels(data):
    hc = category_labels.loadLabeled()
    data['hid'] = data['transaction.category_id'].map(hc.plaid_to_harvest)
    data['hc'] = data['hid'].map(hc.harvest_category_names)
    data['category_labels'] = data['hid'].astype(str).map(hc.harvest_categories)
    return data




if __name__ == '__main__':
    file = "/tmp/transactions-user-transactions-00000-of-00001"
    file = "/tmp/transactions-beam-user-transactions-00000-of-00001"
    file = "/Users/xerox/data/harvest/transactions/15-03-2018-transactions-00000-of-00001"
    data = load(file)
    all_wants = []
    all_want_frac = []
    all_fees = []
    while True:
        try:
            x = next(data)
            try:
                need_amount = x['processed_transactions']['harvest_category_grouped']['Need']['amount']
            except KeyError:
                need_amount = 0
            try:
                want_amount = x['processed_transactions']['harvest_category_grouped']['Want']['amount']
            except KeyError:
                want_amount = 0
            all_wants.append(want_amount)
            if need_amount > 0:
                all_want_frac.append(float(want_amount)/need_amount)
            all_fees.append(x['processed_transactions']['bank_fees']['total'])
        except StopIteration as e:
            break
    all = np.array(all_wants)
    frac = np.array(all_want_frac)
    pdb.set_trace()
    #data = assign_labels(data)
    #all_wants_amount = data[data.category_labels == 'Want']['transaction.amount'].sum()
    #wants_abs_amount = abs(data[data.category_labels == 'Want']['transaction.amount']).sum()
    #print("Wants amount: {}".format(all_wants_amount))
    #print("Absolute wants amount: {}".format(wants_abs_amount))


