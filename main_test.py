# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import main
import unittest
import json


class HarvestComputeTestCase(unittest.TestCase):

    def setUp(self):
        main.app.testing = True
        self.app = main.app.test_client()

        with main.app.app_context():
            pass

    def tearDown(self):
        pass

    def test_process(self):
        with open('data/transactions_mmeli.json', 'r') as f:
            transactions = json.load(f)
            payload = {
                'transactions': transactions,
                'request_options': {
                'daterange': '30_days',
                'misclassified_transactions' : [{
                    'category_id': 23, 
                    'transaction_name_raw': 'jimi crack sauce'
                    }],
                'misclassified_categories' : [{
                    'to_classification': 'need', 
                    'category_id': 23
                    }],
                'transaction_id': 124
                }
            }
            rv = self.app.post('/api/v1/transactions', 
                               data=json.dumps(payload), 
                               follow_redirects=True, 
                               content_type='application/json')
            assert rv.status_code == 200
            assert json.loads(rv.data)['metadata']['request_options']['misclassified_transactions'][0]['transaction_name_raw'], 'jimi crack sauce'

    def test_transactions_cleaned(self):
        with open('data/transactions_mmeli.json', 'r') as f:
            transactions = json.load(f)
            payload = {
                'transactions': transactions,
                'request_options': {
                'daterange': '30_days',
                'transaction_id': 124
                }
            }
            rv = self.app.post('/api/v1/transactions_raw_cleaned', 
                               data=json.dumps(payload), 
                               follow_redirects=True, 
                               content_type='application/json')
            assert rv.status_code == 200


    def test_process_empty(self):
        with open('data/transactions_none.json', 'r') as f:
            transactions = json.load(f)
            payload = {
                'transactions': transactions,
                'request_options': {
                'daterange': '30_days',
                'misclassified_transactions' : [{ 'category_id': 23, 'transaction_name_raw': 'jimi crack sauce'
                    }],
                'misclassified_categories' : [{
                    'to_classification': 'need', 
                    'category_id': 23
                    }],
                'transaction_id': 124
                }
            }
            rv = self.app.post('/api/v1/transactions', 
                               data=json.dumps(payload), 
                               follow_redirects=True, 
                               content_type='application/json')
            assert rv.status_code == 200
            assert json.loads(rv.data)['metadata']['request_options']['misclassified_transactions'][0]['transaction_name_raw'], 'jimi crack sauce'


if __name__ == '__main__':
    unittest.main()
