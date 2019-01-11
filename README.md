# python 3
pip install -r requirements.txt
zip shuffled-full-set-hashed.csv.zip
python webpage.py

# curling
train model, model already exists, please delete model first:

curl -X GET \
    -H "Content-Type: application/json" \
    "http://172.31.40.242:8000/api/v1/train"

test given message:

curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "b44297cf911c 84884d80641d bad6ff5dd7bc bad6ff5dd7bc"}'\
    "http://172.31.40.242:8000/api/v1/predict"

delete model:
curl -X GET \
    -H "Content-Type: application/json" \
    "http://172.31.40.242:8000/api/v1/delete"

# how to use website

The train model has been built using given data, so user can directly test their text in the testarea.
The format of message in testarea should like this(no other symbol):
  b44297cf911c 84884d80641d bad6ff5dd7bc bad6ff5dd7bc

If user want to check the train error rate, please delete model first and then train new model.

User can get confusion matrix using api.


# heavywater
