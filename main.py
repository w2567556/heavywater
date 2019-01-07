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

import logging
import os

from flask import Flask
from flask import request, jsonify

from flask_caching import Cache
app = Flask(__name__)
app.cache = Cache(app, config={'CACHE_TYPE': 'simple'})


from harvest import category_labels
import harvest.transactions_processor as tp
import harvest.bank_fees

import json

@app.cache.cached(timeout=50, key_prefix='harvest_category_classifications')
def load_data():
    return category_labels.loadLabeled()

@app.route('/api/v1/computation', methods = ['POST'])
def process_transactions():
    data = json.loads(request.data)
    app.logger.info('Passed in options:')
    app.logger.info(data['request_options'])
    options = tp.request_options(data['request_options'])
    app.logger.info('Processed_options:')
    app.logger.info(options)
    output = tp.process(data['transactions'], load_data(), options)
    return jsonify(output)


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8181, debug=True)
