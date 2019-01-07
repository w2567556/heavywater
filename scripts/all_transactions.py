import pandas as pd
import json
from pandas.io.json import json_normalize
from harvest import category_labels
import pdb


def load(file):
    with open(file) as f:
        data = []
        for line in f:
            d = json.loads(line)
            data.append(d)
    return pd.io.json.json_normalize(data)

def assign_labels(data):
    hc = category_labels.loadLabeled()
    data['hid'] = data['transaction.category_id'].map(hc.plaid_to_harvest)
    data['hc'] = data['hid'].map(hc.harvest_category_names)
    data['category_labels'] = data['hid'].astype(str).map(hc.harvest_categories)
    return data




if __name__ == '__main__':
    file = "/tmp/transactions-flattened-transactions-00000-of-00001"
    data = load(file)
    data = assign_labels(data)
    all_wants_amount = data[data.category_labels == 'Want']['transaction.amount'].sum()
    wants_abs_amount = abs(data[data.category_labels == 'Want']['transaction.amount']).sum()
    print("Wants amount: {}".format(all_wants_amount))
    print("Absolute wants amount: {}".format(wants_abs_amount))


