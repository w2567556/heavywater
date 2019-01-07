#!/usr/env py
import csv
import numpy as np
import json
import unittest


CLASSIFICATION_VERSION = 2
PLAID_TO_HARVEST_VERSION = 2

class HarvestCategories:
    def __init__(self, harvest_categories, plaid_to_harvest, harvest_category_names, aggregate_stats, version):
        self.version = version
        self.harvest_categories = harvest_categories
        self.plaid_to_harvest = plaid_to_harvest
        self.harvest_category_names = harvest_category_names
        self.aggregate_stats = aggregate_stats

def get_classification_path(version=CLASSIFICATION_VERSION):
    return "data/harvest_category_classification_v{}.json".format(version)

def get_plaid_harvest_conversion_path(version=PLAID_TO_HARVEST_VERSION):
    return "data/plaid_to_harvest_v{}.json".format(version)

def getProbabilityFromClassification(classification):
    if classification == "Need":
        return 0
    elif classification == "Want":
        return 1
    else:
        return 0.5

def getAggregateStats():
    return {
        'want_spend': {
            'avg': 478,
            'std': 500,
            'desc': 'average of want spend across all users'
        },
        'want_frac': {
            'avg': 1.2,
            'std': 2.17,
            'desc': 'average fraction of want to need spend'
        }
    }

def loadLabeled(classification_path=get_classification_path(), plaid_to_harvest_path=get_plaid_harvest_conversion_path(), agg_stats=getAggregateStats()):
    versions = {}
    with open(classification_path ,'r') as file:
        harvest_classification = json.load(file)

    with open(plaid_to_harvest_path ,'r') as file:
        plaid_to_harvest = json.load(file)
    
    versions['plaid_to_harvest'] = plaid_to_harvest['version']
    versions['harvest_classification'] = harvest_classification['version']

    harvest_categories = {}
    harvest_category_names = {}
    for i in harvest_classification['categories']:
        category = i['category']
        classification = i['classification']
        harvest_id = i['harvest_id']
        harvest_categories[harvest_id] = classification
        harvest_category_names[harvest_id] = category

    return HarvestCategories(harvest_categories, plaid_to_harvest['plaid_to_harvest'], harvest_category_names, agg_stats, versions)

def wantsRatio(scores):
    total = len(scores)
    ratio = float(sum(scores))/total
    return ratio

def getSavingsPercent(wantsRatio):
    if wantsRatio <= 0.25:
        return 5
    elif wantsRatio <= 0.5:
        return 10
    elif wantsRatio <= 0.75:
        return 15
    else:
        return 20

def getResponse(wantsRatio):
    print("{} % of your spending is on wants.".format(wantsRatio * 100))
    savingsPercent = round(getSavingsPercent(wantsRatio))
    print("We recommend setting automated investments to {} % ".format(savingsPercent))

class TestLoading(unittest.TestCase):
    def setUp(self):
        pass

    def test_correct_loading(self):
        hc = loadLabeled()
        categories = hc.harvest_categories
        versions = hc.version
        plaid_to_harvest = hc.plaid_to_harvest

        self.assertEqual(versions['harvest_classification'], "2")
        self.assertEqual(versions['plaid_to_harvest'], "2")

        # classification for harvest category
        self.assertEqual(categories['32'], 'Middle Ground')
        self.assertEqual(categories['33'], 'Need')
        self.assertEqual(categories['34'], 'Want')

        # test category name id mapping
        self.assertEqual(hc.harvest_category_names['32'], 'Subscriptions')
        self.assertEqual(hc.harvest_category_names['33'], 'Phone Bills')
        self.assertEqual(hc.harvest_category_names['34'], 'Tourism Related')

        # plaid id to harvest id mapping
        self.assertEqual(len(plaid_to_harvest), 601)
        self.assertEqual(plaid_to_harvest["12008009"], '2')

if __name__ == '__main__':
    #categories = loadLabeled('data/categories_labeled.json')
    #print(categories)
    unittest.main()
