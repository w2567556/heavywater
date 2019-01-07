import pandas as pd
import json
from datetime import datetime
from dateutil import relativedelta as rd
import unittest
from collections import OrderedDict
import harvest.category_labels as catgory_labels
import scipy
import harvest.maths as maths
import harvest
from tabulate import tabulate
from collections import defaultdict
import re
import pdb
import harvest.bank_fees as bank_fees

"""Value of enum is the default value"""
VALID_REQUEST_OPTIONS = {
    'daterange' : '30_days',
    'misclassified_transactions' : [],
    'misclassified_categories' : [],
    'return_df' : False,
    'transaction_id' : ''
}

DATERANGE_READABLE = {
    '30_days' : 'for the past 30 days',
    'all' : 'for as far back as we could go'
}

# change in harvest-ai as well if changing
MISCLASSIFIED_TRANSACTION_HARVEST_CATEGORY_ID = 999
MISCLASSIFIED_TRANSACTION_HARVEST_CATEGORY_NAME = 'Misc'

NAME_OMISSION_RULES = [
    r"online.*transfer.* to",
    r"ach pmt.*",
    r"discover e-payment .*",
    r"payment to .* card",
    r"transfer to .* savings",
    r"eleccheck",
]

NAME_REPLACE_RULES = [
    (r"UBER.*", "Uber"),
    (r"FACEBK.*", "Facebook"), 
    (r"SQU\*SQ \*(.*)", r"\1"),
    (r"SQUARE \*SQ \*(.*)", r"\1"),
    (r"(DELTA AIR).*", r"\1"),
    (r"(Dropbox).*", r"\1"),
    (r"CHECKCARD \d* (.*)", r"\1"),
    (r"(keep the change transfer to acct [\d]*) for .*", r"\1"),
    (r"(AIRBNB) .*", r"\1"),
    (r"\d+", ""),
]


def request_options(options):                        
    """
    Initialize all request options that assumed to exist for processing
    """
    request_options = {}
    for option, default in VALID_REQUEST_OPTIONS.items():
        request_options[option] = options.get(option, default)
    return request_options

def process(plaid_data, loaded_data, processing_options):
    """
    Input data structure:
        {
        'misclassified_categories' -> plaid_id -> need/want
        'misclassified_transactions' -> transaction_id -> [nope]
        'daterange'
        }


    Output data structure:
        [
            metadata
                request_options
                version
            processed_transactions
        ]
        
    """
    output = {
        'metadata': {
            'request_options': processing_options,
            'version': loaded_data.version
        }
    }
    data = pd.DataFrame.from_dict(plaid_data['transactions'])

    # drop columns we're not using
    columns_to_drop=[
        'location', 
        'payment_meta', 
        'account_owner', 
        'transaction_type',
        'category' # will assign harvest category based on id
    ]
    data.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    if (len(data) > 0):
        filtered_cc_data = filter_by_credit_card_accounts(plaid_data['accounts'], data)
        # remove transfers and payments
        filtered_cc_data = filter_name_using_rules(filtered_cc_data, 'name')
        hc = edit_user_categories(processing_options['misclassified_categories'], loaded_data)

        data = processing_pipeline(filtered_cc_data, hc)

        # remove misclassified transactions from the specified category 
        data = reclassify_misclassified_transactions(processing_options['misclassified_transactions'], data)

        # calculate refunds here since we filter on amount after
        refunds = compute_bank_refunds(data)
        #refunds_by_cat = compute_bank_refunds_by_category(data)

        data = data[data['amount'] > 0]
        data.reset_index(drop=True)
    if (len(data) == 0):
        output['metadata']['msg'] = 'Data of length 0'
        return output

    data_within_daterange = filter_to_daterange(data, processing_options['daterange'])
    if (len(data_within_daterange) == 0):
        output['metadata']['msg'] = 'Data within daterange of length 0'

    filtered_discretionary_data = filter_to_discretionary(data_within_daterange)

    processing_output = {}
    processing_output['daterange'] = get_daterange(data_within_daterange, processing_options)

    processing_output['harvest_category_grouped'] = group_by_harvest_category(data_within_daterange)
    processing_output['discretionary'] = discretionary_fraction(filtered_discretionary_data, data_within_daterange)
    processing_output['total_spend'] = data_within_daterange.amount.sum()
    processing_output['user_profile'] = get_user_profile(processing_output)


    # use all the data to get recurrence behavior
    #processing_output['recurrence'] = get_recurrence(data, data_within_daterange)

    processing_output['abnormal_spend'] = get_abonormal_spends(data)
    processing_output['behaviors'] = detect_behaviors(processing_output)
    processing_output['harvest_comparison'] = compare_to_harvest_user(processing_output, hc)
    processing_output['month_pleasure_spend_change'] = get_month_pleasure_spend_percent(data)
    processing_output['bank_fees'] = compute_bank_fees(data, refunds)
    output['processed_transactions'] = processing_output

    if (processing_options['return_df']):
        # to be used for internal analytics
        output['df'] = data_within_daterange

    return output

def compute_bank_refunds_by_category(data):
    x = data.apply(bank_fees.get_fee_refunds_by_category)

def compute_bank_refunds(data):
    refunds = data.name.apply(bank_fees.get_fee_refunds)
    t_refunds = data[refunds != False]
    total = abs(t_refunds.amount.sum())
    filtered_refunds = refunds[refunds != False]
    filtered_refunds = filtered_refunds.rename("type")
    refunds_df = pd.DataFrame(filtered_refunds)
    refunds_df = pd.concat([t_refunds[['date', 'name', 'amount', 'account_id']], refunds_df], axis=1)
    return {
        'total': total,
        'df': refunds_df
    }

def expected_fee_returns(data, refunds):
    refunds_by_account = []
    data['probability_norm'] = data.probability.replace(bank_fees.REFUND_PROBABILITY_NORMALIZED)
    data['exp'] = data.probability_norm * data.amount
    expectedbyacc = data[['account_id', 'exp']].groupby('account_id').sum().to_dict()
    refbyacc = refunds['df'][['account_id', 'amount']].groupby('account_id').sum().to_dict()
    for acc,amount in expectedbyacc['exp'].items():
        # this is a negative number if it exists
        refund = refbyacc['amount'].get(acc, 0)
        refunds_by_account.append((acc, amount + refund))

    refs = sorted(refunds_by_account, key=lambda x: x[1], reverse=True)
    if (len(refs) > 0):
        return refs[0]
    else:
        return []

def compute_bank_fees(data, refunds):
    out = {}
    fees = data.name.apply(bank_fees.get_bank_fee_type)
    t_fees = data[fees != False]
    total = t_fees.amount.sum() - refunds['total']
    filtered_fees = fees[fees != False]
    filtered_fees = filtered_fees.rename("type")
    fees_df = pd.DataFrame(filtered_fees)
    fees_df['probability'] = fees_df.type.replace(bank_fees.REFUND_PROBABILITIES)
    fees_df.type = fees_df.type.apply(lambda x: x.value)
    fees_df = pd.concat([t_fees[['date', 'name', 'amount', 'account_id']], fees_df], axis=1)
    out['refund_account'] = expected_fee_returns(fees_df, refunds)
    # drop account ids after refund computation
    fees_df.drop(['account_id'], inplace=True, axis=1)
    fees_dict = fees_df.groupby('type').apply(lambda x: x.to_dict(orient='records'))
    out['total'] = total
    out['transactions'] = t_fees[['date', 'name', 'amount']].to_dict(orient='records')
    out['transactions_grouped'] = []
    for f in bank_fees.BANK_FEES:
        val = {'type': f.value}
        try:
            val['fees'] = fees_dict[f.value]
        except KeyError:
            val['fees'] = []
        out['transactions_grouped'].append(val)
    return out

def compare_to_harvest_user(data, hc):
    try:
        need_amount = data['harvest_category_grouped']['Need']['amount']
    except KeyError:
        need_amount = 0
    try:
        want_amount = data['harvest_category_grouped']['Want']['amount']
    except KeyError:
        want_amount = 0
    if need_amount > 0:
        want_frac = float(want_amount)/need_amount
    else:
        want_frac = 1

    avg = hc.aggregate_stats['want_spend']['avg']
    want_diff_percent = float(want_amount - avg) / avg * 100
    return {
        'want_diff_percent': want_diff_percent,
        'want_frac_diff': want_frac - hc.aggregate_stats['want_frac']['avg']
    }

def detect_behaviors(processed):
    out = []
    # over 10 times on want or need categories
    try:
        want_categories = processed['harvest_category_grouped']['Want']['categories']
        wants_by_count = sorted(want_categories, key=lambda k: k['count'], reverse=True)
        top_want = next(iter(wants_by_count), None)
        if top_want['count'] > 10:
            out.append({
                'type': 'over_10_times',
                'data': {
                    'amount' : top_want['amount'],
                    'count' : top_want['count'],
                    'category' : top_want['category'],
                    'on': 'Want'
                }
            })
        else: 
            need_categories = processed['harvest_category_grouped']['Need']['categories']
            needs_by_count = sorted(need_categories, key=lambda k: k['count'], reverse=True)
            top_need = next(iter(needs_by_count), None)
            if top_need['count'] > 10:
                out.append({
                    'type': 'over_10_times',
                    'data': {
                        'amount' : top_want['amount'],
                        'count' : top_want['count'],
                        'category' : top_want['category'],
                        'on': 'Want'
                    }
                })
    except KeyError:
        pass

    return out


def edit_user_categories(misclassified_categories, hc):
    for c in misclassified_categories:
        hc.harvest_categories[str(c['category_id'])] = get_classification(c['to_classification'])
    return hc

def get_classification(c):
    dict =  {
        'need': 'Need',
        'want': 'Want',
        'middle ground': 'Middle Ground'
    }
    return dict.get(c.lower().strip())


def reclassify_misclassified_transactions(misclassified_transactions, data):
    ts = [t['transaction_name_raw'] for t in misclassified_transactions]
    tsp = replace_name_using_rules(pd.Series(ts))
    idx = data[data.name_processed.isin(tsp)].index
    data.loc[idx, 'category_labels'] = 'Middle Ground'
    data.loc[idx, 'harvest_category_id'] = MISCLASSIFIED_TRANSACTION_HARVEST_CATEGORY_ID
    data.loc[idx, 'harvest_category'] = MISCLASSIFIED_TRANSACTION_HARVEST_CATEGORY_NAME
    return data

def get_user_profile(data):
    # make sure to check all keys referenced here exist in all cases
    try:
        pleasure_amount = data['harvest_category_grouped']['Want']['amount']
        pleasure_category = data['harvest_category_grouped']['Want']['categories'][0]['category']
    except KeyError:
        pleasure_amount = 0
        pleasure_category = ""
        
    # spent < 100 on pleasures
    if pleasure_amount < 100:
        return {
            'type': 'money_savvy',
            'name': 'The Super Savant!',
            'desc': 'Hat tip! You are so disciplined with money we are jealous! Time we talk about how to grow your money, shall we?'
        }
    elif pleasure_category == "Restaurants":
        return {
            'type': 'socialite',
            'name': 'The Gorgeous Gourmand!',
            'desc': 'You love eating out, and people who love to eat are always the best people.'
        }
    elif pleasure_category == "Bars":
        return {
            'type': 'pourfectionist',
            'name': 'The Pourfectionist',
            'desc': 'We love you, and we love those pours you love. We promise we will only help you count your money, not the glasses of wine you had last month.'
        }
    elif pleasure_category in ["Beauty Products", "Peronsal Care"]:
        return {
            'type': 'beauty_boss',
            'name': 'The Beauty Boss',
            'desc': 'Beauty is power - we love that you’re embracing it!'
        }
    elif pleasure_category in ["Shops", "Clothing and Accessories"]:
        return {
            'type': 'shoptimist',
            'name': 'The Shoptimist',
            'desc': 'For you, the store is always full of wonders.'
        }
    elif pleasure_category in ["Travel"]:
        return {
            'type': 'traveller',
            'name': 'The Wonderful Wanderer',
            'desc': 'You were bit by the travel bug this month. You must have many interesting stories. Share some with us!'
        }
    elif pleasure_category in ["Taxi"]:
        return {
            'type': 'rider',
            'name': 'The Ritzy Rider',
            'desc': 'You travel in style. The taxi companies love you. We love you more!'
        }
    elif pleasure_category in ["Home Decor"]:
        return {
            'type': 'interior_designer',
            'name': 'The Apartment Therapist',
            'desc': 'Whatever your home decor style, we are sure you’re crushing it!'
        }
    else: 
        return {
            'type': 'harvest_default',
            'name': 'The Harvest Muse',
            'desc': 'We cannot put you in a box. Your lifestyle inspires creativity. Cheers to you!'
        }


def group_by_harvest_category(data):
    data.set_index(['category_labels', 'harvest_category', 'name_processed'], inplace=True)
    g0 = data.groupby(level='category_labels')
    g1 = data.groupby(level='harvest_category')
    g2 = data.groupby(level='name_processed')
     
    a0 = g0.aggregate({'amount': ['sum', 'count']}).reset_index().sort_values(by=[('amount', 'sum')], ascending=False)
    a1 = g1.aggregate({'amount': ['sum', 'count']}).reset_index().sort_values(by=[('amount', 'sum')], ascending=False)
    a2 = g2.aggregate({'amount': ['sum', 'count']}).reset_index().sort_values(by=[('amount', 'sum')], ascending=False)

    # need something to give mapping from category to classification
    dd = data.reset_index()
    cat2label = dd[['harvest_category', 'category_labels']].set_index('harvest_category').to_dict()['category_labels']
    t2cat = dd[['harvest_category', 'name_processed']].set_index('name_processed').to_dict()['harvest_category']
    cat2id = dd[['harvest_category', 'harvest_category_id']].set_index('harvest_category').to_dict()['harvest_category_id']
    trans2id = dd[['name_processed', 'harvest_category_id']].set_index('name_processed').to_dict()['harvest_category_id']
    trans2nameraw = dd[['name_processed', 'name']].set_index('name_processed').to_dict()['name']

    classifications = {}
    for record in a0.to_dict(orient='records'):
        classification = record[('category_labels', '')]
        amount = record[('amount', 'sum')]
        count = record[('amount', 'count')]
        classifications[classification] = {
            'classification': classification,
            'amount': amount,
            'count': count,
        }

    categories = []
    for record in a1.to_dict(orient='records'):
        category = record[('harvest_category', '')]
        amount = record[('amount', 'sum')]
        count = record[('amount', 'count')]
        c = {
            'category': category,
            'category_id': cat2id[category],
            'amount': amount,
            'count': count,
            'transactions': []
        }
        categories.append(c)

    transactions = []
    for record in a2.to_dict(orient='records'):
        transaction = record[('name_processed', '')]
        amount = record[('amount', 'sum')]
        count = record[('amount', 'count')]
        t = {
            'transaction': transaction,
            'harvest_category_id': trans2id[transaction],
            'transaction_name_raw': trans2nameraw[transaction],
            'amount': amount,
            'count': count
        }
        transactions.append(t)

    cat_with_transactions = defaultdict(list)
    for t in transactions:
        cat_with_transactions[t2cat[t['transaction']]].append(t)

    labels_with_categories = defaultdict(list)
    for c in categories:
        c['transactions'] = cat_with_transactions[c['category']]
        labels_with_categories[cat2label[c['category']]].append(c)

    for k,c in classifications.items():
        c['categories'] = labels_with_categories[c['classification']]

    return classifications

def discretionary_fraction(disc, all):
    output = {}
    disc_total = sum(disc['amount'])
    all_filtered = all[all['amount'] > 0]
    total = sum(all_filtered['amount'])
    output['discretionary_amount'] = dec(disc_total)
    if total > 0:
        disc_percent = dec(float(disc_total)/total*100)
    else:
        disc_percent = 0
    output['discretionary_percent'] = disc_percent
    output['discretionary_five_year_snp_amount'] = dec(maths.example_monthly_snp_future_value(disc_total*0.25, 5))
    output['discretionary_five_year_savings_amount'] = dec(maths.example_monthly_savings_future_value(disc_total*0.25, 5))
    output['discretionary_desc'] = '0.25 of discretionary spend over five years using half of the past 5 year snp500 returns'
    return output

def sort_top_days(data):
    count = data.groupby('day_of_week')[['amount']].count()
    return count_to_dict(count)

def sort_top_days_amount(data):
    amount_sum = data.groupby('day_of_week')[['amount']].sum()
    amount_sum.reset_index(level=0, inplace=True)
    out = amount_sum[amount_sum.amount > 0].sort_values(by='amount', ascending=False).head(3).round(2)
    return out.to_dict('records')

def get_daterange(data, processing_options):
    end = max(data['datetime'])
    start = min(data['datetime'])
    duration_days = (end-start).days
    return {
        'end' : end.strftime('%b %d, %Y'),
        'start' : start.strftime('%b %d, %Y'),
        'duration_days' : duration_days,
        'desc': DATERANGE_READABLE.get(processing_options['daterange'])
    }

def filter_to_daterange(data, daterange):
    end = max(data['datetime'])
    if daterange == '30_days':
        start = end-pd.Timedelta(30, unit='d')
    if daterange == 'all':
        start = min(data['datetime'])
    return data[(data['datetime'] > start) & (data['datetime'] <= end)]


def filter_to_discretionary(data):
    return data[data['category_labels'] == 'Want']

def filter_by_credit_card_accounts(accounts, transactions):
    credit_card_accounts = []
    for account in accounts:
        if account['type'] == 'credit' or account['type'] == 'depository':
            credit_card_accounts.append(account['account_id'])
    cc = transactions['account_id'].isin(credit_card_accounts)
    return transactions[cc].reset_index(drop=True)

def count_to_dict(df, top_n=5):
    df.reset_index(level=0, inplace=True)
    out = df.sort_values(by="amount", ascending=False).head(top_n).round(2)
    out.rename(columns={"amount":"count"}, inplace=True)
    return out.to_dict('records')


def sort_top_categories(data, index='top_category'):
    count = data[~data[index].str.contains('<Unclassified>')].reset_index(drop=True).groupby(index)[['amount']].count()
    return count_to_dict(count)

def sort_top_category_amount(data, index='top_category'):
    d2 = data[~data[index].str.contains('<Unclassified>')].reset_index(drop=True)
    amount_sum = d2.groupby(index)[['amount']].sum()
    amount_sum.reset_index(level=0, inplace=True)
    out = amount_sum[amount_sum.amount > 0].sort_values(by='amount', ascending=False).head(3).round(2)
    return out.to_dict('records')

def sort_top_names(data, index='name'):
    count = data.groupby(index)[['amount']].count()
    return count_to_dict(count, top_n=10)

def sort_top_names_amount(data, index='name'):
    amount_sum = data.groupby(index)[['amount']].sum()
    amount_sum.reset_index(level=0, inplace=True)
    out = amount_sum[amount_sum.amount > 0].sort_values(by='amount', ascending=False).head(10).round(2)
    return out.to_dict('records')

def get_month_pleasure_spend_percent(data):
    data = data[data['category_labels'] == 'Want']
    if (len(data) > 0):
        data.index = pd.to_datetime(data['date'])
        months = data.groupby(pd.Grouper(freq='M'))
        monthly = months['amount'].sum().sort_index(ascending=False)
        till_last_month = monthly.drop(monthly.index[0])
        this_month = monthly.iloc[0]
        avg_last_month = till_last_month.mean()
        if avg_last_month > 0:
            return ((this_month - avg_last_month) / (avg_last_month) * 100)
        else:
            return 0
    else:
        return 0

def get_abonormal_spends(data):
    # most spends for this daterange
    # maybe percent of total spend

    # define abnormal as 1. not seen before 2. larger quantity than seen before
    pass

def get_recurrence(data, data_within_daterange):
    recurrence = []
    for name, df in data.groupby('name_processed'):
        if len(df) > 1:
            first_date = datetime.strptime(df.iloc[0]['date'], "%Y-%m-%d")
            # last date that was seen
            last_date = first_date
            # skip the first entry
            iterrows = df.iterrows()
            next(iterrows)
            for index, row in iterrows:
                current_date = datetime.strptime(row['date'], "%Y-%m-%d")
                r = rd.relativedelta(last_date, current_date)
                delta = last_date - current_date
                if delta:
                    recurrence.append({'name':name, 'delta_days': (last_date - current_date).days, 'relative_delta':r})
                # after all other operations
                last_date = current_date

    recurrence_df = pd.DataFrame.from_records(recurrence)

    #occurence = []
    #for name, df in recurrence_df.groupby('name'):
    #    days_frequency = df.groupby('delta_days').size().to_dict()
    #    for day, count in days_frequency.items():
    #        occurence.append({'name': name, 'occurs_every_days': day, 'number_of_times_occurred': count})

    #occurrence_df = pd.DataFrame.from_records(occurence)
    #occurrence_df = occurrence_df.set_index('name')
    monthly = recurrence_df[recurrence_df['relative_delta'] == rd.relativedelta(months=+1)]['name']
    monthly_noshow = monthly[~monthly.isin(data_within_daterange.reset_index()['name_processed'])]
    return monthly_noshow

def get_unclassified_fraction(data):
    categories = data['category']
    unclassified = categories.isnull().sum()
    return dec(float(unclassified)/len(categories))

def get_top_category(arr):
    if arr:
        return arr[0]
    else:
        return "<Unclassified>"
    
def get_flattened_category(arr):
    if arr:
        return ",".join(arr)
    else:
        return "<Unclassified>"

def get_day_of_week(date):
    days = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]
    day = datetime.weekday(datetime.strptime(date, "%Y-%m-%d"))
    return days[day]


def replace_name_using_rules(series):
    out = series.copy()
    for regex, replace in NAME_REPLACE_RULES:
        out.replace(regex=re.compile(regex, flags=re.IGNORECASE), value=replace, inplace=True)
    return out

def filter_name_mask(series):
    out = series.copy()
    mask = pd.Series([False]*len(out))
    for regex in NAME_OMISSION_RULES:
        mask = mask | out.str.contains(regex, flags=re.IGNORECASE, regex=True)
    return mask

def filter_name_using_rules(df, col):
    mask = filter_name_mask(df[col])
    df = df[~mask]
    return df



def processing_pipeline(data, hc):
    data['harvest_category_id'] = data['category_id'].map(hc.plaid_to_harvest)
    data['harvest_category'] = data['harvest_category_id'].map(hc.harvest_category_names)
    data['category_labels'] = data['harvest_category_id'].map(hc.harvest_categories)
    data['datetime'] = pd.to_datetime(data['date'])
    data['day_of_week'] = data['date'].map(get_day_of_week)
    data['name'] = data['name'].str.strip()
    data['name_processed'] = replace_name_using_rules(data['name'])

    #print(tabulate(data[['name_processed', 'category_id', 'harvest_category']], headers='keys', tablefmt='psql'))
    return data

def dec(n):
    return '{0:.2f}'.format(n)

class TestProcessor(unittest.TestCase):

    def setUp(self):
        with open('data/transactions_mmeli.json', 'r') as f:
            self.fixture_mmeli = json.load(f)
        self.loaded_data = harvest.category_labels.loadLabeled()

    def testRequestOptions(self):
        with open('data/transactions_refund.json', 'r') as f:
            fixture = json.load(f)
        loaded_data = harvest.category_labels.loadLabeled()
        payload = request_options({})
        data = process(fixture, self.loaded_data, payload)
        print(data)

    def testRequestOptions(self):
        null_options = {}
        options = request_options(null_options)
        self.assertEqual(options['daterange'], '30_days')

        value_options = {'daterange': 'all'}
        options = request_options(value_options)
        self.assertEqual(options['daterange'], 'all')
        self.assertEqual(options['misclassified_transactions'], [])

    def testReplaceRules(self):
        data = pd.Series.from_array([
            'SQU*SQ *COFFEED CHELSE',
            'UBER TRIP KP673',
            'FACEBK 4ADAEDEJ22',
            'SQuaRE *SQ *IDEA COFFE',
            'CHECKCARD 0120 OLEANA RESTAURANT CAMBRIDGE MA',
            'Dropbox*HG7KFQBT4HVM',
            'DROPBOX*86GLGPB8D33H DROPBOX.COM CA 24692168013100312940852 RECURRING',
            'DELTA AIR 0062310351418DELTA.COM',
            'KEEP THE CHANGE TRANSFER TO ACCT 0124 FOR 01/29/18',
            'AIRBNB * HMH9M2DFMW'
        ])
        replaced = replace_name_using_rules(data).tolist()
        valid_output = [
            'COFFEED CHELSE',
            'Uber',
            'Facebook',
            'IDEA COFFE',
            'OLEANA RESTAURANT CAMBRIDGE MA',
            'Dropbox',
            'DROPBOX',
            'DELTA AIR',
            'KEEP THE CHANGE TRANSFER TO ACCT ',
            'AIRBNB'
        ]
        self.assertEqual(replaced, valid_output)

    def testOmissionRules(self):
        data = pd.Series.from_array([
            'HEAD',
            'Online Banking transfer to CHK 4981 Confirmation# 5140903013',
            'AMERICAN EXPRESS DES:ACH PMT ID:M0952',
            'DISCOVER E-PAYMENT 9318 WEB',
            'Online Transfer to CHK ...7870 transaction#: 6839901100 01/22',
            'Payment to Chase card ending in',
            'Transfer to Citi Savings 06:13a #9998 ONLINE Reference # 000526',
            'ElecCheck 197 KBL DES:CHECK PMTS CHECK #:0197',
            'TAIL'

        ]).to_frame()
        omitted = filter_name_using_rules(data, 0)[0].tolist()
        valid_output = [
            'HEAD',
            'TAIL'
        ]
        self.assertEqual(omitted, valid_output)

    def testProcessing(self):
        payload = request_options({})
        data = process(self.fixture_mmeli, self.loaded_data, payload)
        categories = data['processed_transactions']['harvest_category_grouped']['Want']['categories']
        self.assertEqual(data['metadata']['request_options']['daterange'], '30_days')
        self.assertAlmostEqual(data['processed_transactions']['harvest_category_grouped']['Need']['amount'], 876.72)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Need']['count'], 37)
        self.assertAlmostEqual(data['processed_transactions']['harvest_category_grouped']['Want']['amount'], 1353.1)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Want']['count'], 75)
        self.assertEqual(len(categories), 8)
        self.assertEqual(categories[0]['category'], 'Restaurants')
        self.assertEqual(categories[0]['category_id'], '6')
        self.assertEqual(categories[0]['amount'], 679.88)
        self.assertEqual(categories[0]['count'], 16)
        self.assertEqual(len(categories[0]['transactions']), 13)
        self.assertEqual(categories[0]['transactions'][0]['transaction'], 'OLEANA RESTAURANT CAMBRIDGE MA ')
        self.assertEqual(categories[0]['transactions'][0]['harvest_category_id'], '6')
        self.assertEqual(categories[0]['transactions'][0]['count'], 1)
        self.assertEqual(categories[0]['transactions'][0]['amount'], 173.38)
        self.assertAlmostEqual(data['processed_transactions']['total_spend'], 3485.29)
        self.assertAlmostEqual(data['processed_transactions']['bank_fees']['total'], 34.23)
        self.assertEqual(data['processed_transactions']['bank_fees']['refund_account'][0], 'YEL90yRKzaF93EoJda4dFJ5KakEjxmtrBKX3M')
        self.assertAlmostEqual(data['processed_transactions']['bank_fees']['refund_account'][1], 4.923)
        self.assertEqual(data['processed_transactions']['bank_fees']['transactions'][0]['date'], '2018-01-29')
        self.assertEqual(data['processed_transactions']['bank_fees']['transactions_grouped'][1]['fees'][0]['probability'], 'Low')

    def testProcessingWithMisclassifiedTransactions(self):
        payload = request_options({
            'misclassified_transactions': [
                {
                    'category_id': 61,
                    'transaction_name_raw': "#07589 STAR MA 01/15 #000620923 PURCHASE #07589 STAR MARKE"
                },
                {
                    'category_id': 6,
                    'transaction_name_raw': "CHECKCARD 0201 CLOVER FOOD LAB CAMBRIDGE MA 24492158032741374546390"
                }
            ]
        })
        data = process(self.fixture_mmeli, self.loaded_data, payload)
        categories = data['processed_transactions']['harvest_category_grouped']['Want']['categories']
        self.assertEqual(data['metadata']['request_options']['daterange'], '30_days')
        self.assertAlmostEqual(data['processed_transactions']['harvest_category_grouped']['Need']['amount'], 743.88)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Need']['count'], 35)
        self.assertAlmostEqual(data['processed_transactions']['harvest_category_grouped']['Want']['amount'], 1353.1 - 9.50)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Want']['count'], 74)
        self.assertEqual(len(categories), 8)
        self.assertEqual(categories[0]['category'], 'Restaurants')
        self.assertEqual(categories[0]['category_id'], '6')
        self.assertAlmostEqual(categories[0]['amount'], 679.88 - 9.50)
        self.assertEqual(categories[0]['count'], 15)
        self.assertEqual(len(categories[0]['transactions']), 12)
        self.assertEqual(categories[0]['transactions'][0]['transaction'], 'OLEANA RESTAURANT CAMBRIDGE MA ')
        self.assertEqual(categories[0]['transactions'][0]['harvest_category_id'], '6')
        self.assertEqual(categories[0]['transactions'][0]['count'], 1)
        self.assertEqual(categories[0]['transactions'][0]['amount'], 173.38)
        f_categories = data['processed_transactions']['harvest_category_grouped']['Middle Ground']['categories']
        self.assertEqual(f_categories[0]['category'], MISCLASSIFIED_TRANSACTION_HARVEST_CATEGORY_NAME)
        self.assertEqual(f_categories[0]['count'], 3)
        self.assertEqual(f_categories[0]['transactions'][0]['amount'], 132.84)
        self.assertAlmostEqual(data['processed_transactions']['harvest_comparison']['want_diff_percent'], 181.088, places = 3)

    def testProcessingWithMisclassifiedCategories(self):
        payload = request_options({
            'misclassified_categories': [
                {
                    'category_id': 65,
                    'to_classification': 'Want'
                },
                {
                    'category_id': 6,
                    'to_classification': 'Need'
                }
            ]
        })
        data = process(self.fixture_mmeli, self.loaded_data, payload)
        categories = data['processed_transactions']['harvest_category_grouped']['Want']['categories']
        self.assertEqual(data['metadata']['request_options']['daterange'], '30_days')
        self.assertAlmostEqual(data['processed_transactions']['harvest_category_grouped']['Need']['amount'], 1352.13)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Need']['count'], 31)
        self.assertAlmostEqual(data['processed_transactions']['harvest_category_grouped']['Want']['amount'], 877.69)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Want']['count'], 81)
        self.assertEqual(len(categories), 8)
        self.assertEqual(categories[0]['category'], 'Shops')
        self.assertEqual(categories[0]['category_id'], '60')

    def testExpandingDaterange(self):
        # default daterange, aka 30 days
        payload = request_options({})
        data = process(self.fixture_mmeli, self.loaded_data, payload)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Need']['count'], 37)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Want']['count'], 75)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Middle Ground']['count'], 2)
        self.assertEqual(data['metadata']['request_options']['daterange'], '30_days')


        # all dateranges
        payload = request_options({
            'daterange': 'all'
        })
        data = process(self.fixture_mmeli, self.loaded_data, payload)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Need']['count'], 117)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Want']['count'], 168)
        self.assertEqual(data['processed_transactions']['harvest_category_grouped']['Middle Ground']['count'], 5)
        self.assertEqual(data['metadata']['request_options']['daterange'], 'all')

if __name__ == "__main__":
    unittest.main()
    #with open('data/transactions_mmeli.json', 'r') as f:
    #    data_dict = json.load(f)
    #    loaded_data = harvest.category_labels.loadLabeled()
    #    data = process(data_dict, loaded_data, request_options({
    #        'misclassified_transactions': [{
    #            'category_id': 61,
    #            'transaction_name_raw': "#07589 STAR MA 01/15 #000620923 PURCHASE #07589 STAR MARKE"
    #        }]
    #    }))
    #    print(json.dumps(data))

