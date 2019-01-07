import pandas as pd
import json
from pandas.io.json import json_normalize
from harvest import category_labels
from harvest import bank_fees
from harvest import transactions_processor as tp
import pdb
import numpy as np


def load(file):
    hc = category_labels.loadLabeled()
    institutions = bank_fees.institutionsNameMap()
    with open(file) as f:
        for line in f:
            dp = json.loads(line)
            if dp:
                val = tp.process(dp[1]['transactions-raw'], hc, tp.request_options({'daterange': 'all', 'return_df': True}))
                val['institution'] = institutions[dp[1]['transactions-raw']['item']['institution_id']]
                yield val

if __name__ == '__main__':
    file = "/Users/xerox/data/harvest/transactions/12-05-2018-transactions-00000-of-00001"
    file = "/Users/xerox/data/harvest/transactions/12-25-2018-transactions-00000-of-00001"
    collected = []
    allfees = []
    feesvsspends = []
    wantsbymonth = pd.DataFrame()
    needsbymonth = pd.DataFrame()
    totalbymonth = pd.DataFrame()
    feesbymonth = pd.DataFrame()
    feesvswants = []
    for data in load(file):
        if ('df' not in data):
            continue
        df = data['df']
        df.reset_index(inplace=True)
        df['month'] = df['datetime'].apply(lambda x: x.strftime("%y/%m"))
        cats = df[['month', 'amount', 'category_labels']].groupby(['category_labels', 'month']).sum()
        df['fees'] = df.name.apply(bank_fees.get_bank_fees)
        df['bank'] = data['institution']
        filtered = df[df.fees != False]
        feesgrouped = filtered[['month', 'amount', 'fees', 'bank']].groupby(['month', 'fees', 'bank']).sum()
        feesbymonth = pd.concat([feesbymonth, feesgrouped])

        if (len(filtered) > 0):
            # users' monthly fees vs spends
            f = filtered[['month', 'amount']].groupby('month').sum()
            s = df[['month', 'amount']].groupby('month').sum()
            d = pd.concat([s,f], axis=1)
            d.to_csv('feesvsspends', mode='a', header=True)
            feesvsspends.append(d)


        totalbymonth = pd.concat([totalbymonth, df[['month', 'amount']].groupby('month').sum()])
        try: 
            wantsbymonth = pd.concat([wantsbymonth, cats.loc['Want']])
        except KeyError:
            pass
        try:
            needsbymonth = pd.concat([needsbymonth, cats.loc['Need']])
        except KeyError:
            pass
        try:
            totalbymonth = pd.concat([totalbymonth, cats.loc['Need']])
        except KeyError:
            pass
        d = {}
        try:
            d['need'] = data['processed_transactions']['harvest_category_grouped']['Need']['amount']
        except KeyError:
            d['need'] = 0

        try:
            d['want'] = data['processed_transactions']['harvest_category_grouped']['Want']['amount']
        except KeyError:
            d['want'] = 0

        try:
            d['bank_fees'] = data['processed_transactions']['bank_fees']['total']
        except KeyError:
            d['bank_fees'] = 0
        collected.append(d)

        feesvswants.append({'fee': filtered['amount'].sum(), 'want': d['want']})

        try:
            for fee in data['processed_transactions']['bank_fees']['transactions_grouped']:
                if fee['fees']:
                    for f in fee['fees']:
                        allfees.append(f)
        except KeyError:
            pass

    df = pd.DataFrame(collected)
    df1 = pd.DataFrame(allfees)


    total = len(df)
    withbankfees = len(df[df.bank_fees > 0])
    print('total users:\t', total)
    print('total users with bank fees:\t', withbankfees)
    print('% users with bank fees:\t', float(withbankfees / total) * 100)
    print('bank fees stats:\n', df[df.bank_fees > 0].bank_fees.describe())
    print('bank fees correlations:\n', df.corr())
    print('bank fees summaries:\n', df1.groupby('type').describe())
    # percents of different kind of fees
    print(feesbymonth.groupby('bank').describe())
    print('fees by type', feesbymonth.groupby('fees').sum() / feesbymonth.sum() * 100)
    import pdb; pdb.set_trace()
