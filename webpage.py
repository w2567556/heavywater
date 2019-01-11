from flask import Flask, Config as BaseConfig, jsonify, render_template, redirect, request
import json, time
from main import train_model, test_model
import pandas as pd
from scripts.delete import delete_tmp
from scripts.json_transform import NumpyEncoder
DRIVERS = {}

app = Flask(__name__)
dictionary = None
lsi_model = None
predictor = None
train_err_ratio = None
train_cm = None
test_err_ratio = None
test_cm = None
consume_time_train = None

@app.route('/')
def root():
    return render_template('front.html')

@app.route('/trainModel', methods = ['GET'])
def train():
    dictionary, lsi_model, predictor, train_err_ratio, train_cm, test_err_ratio, test_cm, consume_time_train = train_model()
    return render_template('metrics.html',  train_err_ratio=train_err_ratio, train_cm=train_cm, test_err_ratio=test_err_ratio, test_cm=test_cm, consume_time=consume_time_train)

@app.route('/deleteModel', methods = ['GET'])
def delete():
    delete_tmp()
    return render_template('ok.html')


@app.route('/testText', methods = ['POST'])
def result():
    try:
        demo_doc = request.form.get('mytextarea')
    except:
        demo_doc = None

    result, consume_time_test = test_model(dictionary, lsi_model, predictor, demo_doc)

    return render_template('prediction.html', result=result, consume_time=consume_time_test)


@app.route('/api/v1/train', methods = ['GET'])
def train_api():
    dictionary, lsi_model, predictor, train_err_ratio, train_cm, test_err_ratio, test_cm, consume_time_train = train_model()
    output = {}
    output['train_err_ratio'] = train_err_ratio
    output['train_cm'] = train_cm
    output['test_err_ratio'] = test_err_ratio
    output['test_cm'] = test_cm
    output['consume_time'] = consume_time_train
    responses = json.dumps(output)#jsonify(json.dumps(output, cls=NumpyEncoder))
    return responses

@app.route('/api/v1/delete', methods = ['GET'])
def delete_api():
    delete_tmp()
    output = {}
    output['messgae'] = 'ok'
    responses = jsonify(output)
    responses.status_code = 200
    return responses

@app.route('/api/v1/predict', methods = ['POST'])
def result_api():
    try:
        test_json = request.get_json()
        demo_doc = test_json['message']
    except:
        demo_doc = None
    if demo_doc is None:
        return jsonify({})
    else:
        output = {}
        result, consume_time_test = test_model(dictionary, lsi_model, predictor, demo_doc)
        output['class'] = result
        output['consume_time(s)'] = consume_time_test
        responses = jsonify(output)
        responses.status_code = 200
        return responses

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
