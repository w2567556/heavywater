# python 3
pip install -r requirements.txt
unzip shuffled-full-set-hashed.csv.zip
python webpage.py

# curling
train model, model already exists, please delete model first:

curl -X GET \
    -H "Content-Type: application/json" \
    "http://18.222.196.57:8000/api/v1/train"

test given message:

curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"message": "b44297cf911c 84884d80641d bad6ff5dd7bc bad6ff5dd7bc"}'\
    "http://18.222.196.57:8000/api/v1/predict"

delete model:
curl -X GET \
    -H "Content-Type: application/json" \
    "http://18.222.196.57:8000/api/v1/delete"

# how to use website
url for website http://18.222.196.57:8000

The train model has been built using given data and sample rate is 10, and the error rate is 0.23. But if you use local machine or select a server which has a larger memory to run the program with sample rate = 1, the accuracy can reach 0.17.

User can directly test their text in the testarea.

The format of message in testarea should like this(no other symbol):
  b44297cf911c 84884d80641d bad6ff5dd7bc bad6ff5dd7bc

If user want to check the train error rate, please delete model first and then train new model.

User can get confusion matrix using api.

# output

The number of trees in random forest :1500
train error: 0.005
confusion matrix for training  [[3846, 0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 2], [0, 506, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 186, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 178, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 15292, 14, 2, 0, 1, 0, 10, 1, 2, 6], [1, 0, 0, 0, 11, 8462, 0, 0, 3, 0, 14, 1, 0, 1], [0, 0, 0, 0, 13, 5, 205, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 602, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 3, 0, 0, 721, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 3525, 1, 0, 0, 2], [1, 0, 0, 0, 0, 8, 0, 0, 0, 0, 7197, 0, 0, 1], [20, 3, 1, 0, 37, 22, 0, 2, 0, 5, 23, 642, 0, 21], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 567, 0], [2, 0, 0, 0, 5, 0, 0, 0, 0, 4, 2, 0, 0, 7693]]
test error: 0.176
confusion matrix for testing  [[821, 0, 0, 0, 1, 7, 0, 1, 1, 11, 2, 5, 0, 126], [0, 58, 0, 0, 0, 6, 0, 0, 0, 7, 0, 0, 0, 46], [0, 2, 16, 0, 11, 2, 0, 0, 0, 3, 2, 0, 0, 6], [0, 0, 0, 14, 7, 8, 0, 0, 0, 0, 19, 0, 0, 0], [2, 0, 2, 0, 3250, 143, 9, 4, 0, 6, 72, 8, 7, 137], [3, 1, 0, 0, 117, 1759, 1, 5, 23, 20, 146, 9, 7, 43], [0, 0, 0, 0, 30, 14, 10, 0, 0, 0, 12, 0, 0, 0], [0, 0, 0, 0, 26, 13, 0, 96, 0, 0, 9, 2, 0, 1], [1, 0, 0, 0, 0, 36, 0, 0, 116, 1, 10, 0, 0, 1], [5, 1, 0, 0, 21, 20, 0, 0, 0, 701, 8, 3, 1, 79], [1, 0, 0, 0, 46, 144, 0, 1, 0, 1, 1558, 8, 0, 7], [1, 0, 0, 0, 36, 47, 0, 0, 1, 2, 87, 13, 0, 5], [3, 0, 0, 0, 35, 7, 0, 0, 0, 8, 1, 2, 101, 9], [81, 0, 1, 0, 166, 63, 0, 3, 0, 49, 19, 2, 0, 1641]]

The number of trees in random forest :100
train error: 0.005
confusion matrix for training  [[3860, 0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 1], [0, 504, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 177, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 180, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 15225, 17, 2, 0, 0, 0, 11, 0, 1, 6], [1, 0, 0, 0, 10, 8561, 0, 0, 3, 0, 13, 0, 1, 1], [0, 0, 0, 0, 12, 5, 211, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 587, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 5, 0, 0, 737, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 3528, 1, 0, 1, 1], [1, 0, 0, 0, 2, 7, 0, 0, 0, 0, 7191, 0, 0, 0], [17, 1, 1, 0, 36, 23, 0, 1, 1, 3, 23, 622, 1, 17], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 591, 0], [5, 0, 0, 0, 5, 0, 0, 0, 0, 2, 2, 0, 0, 7714]]
test error: 0.177
confusion matrix for testing  [[823, 1, 0, 0, 1, 12, 0, 0, 0, 6, 4, 5, 0, 110], [1, 68, 1, 0, 2, 4, 0, 0, 0, 4, 0, 0, 0, 40], [1, 0, 13, 0, 11, 1, 0, 0, 0, 2, 3, 0, 0, 20], [0, 0, 0, 18, 2, 11, 0, 0, 0, 0, 16, 0, 0, 0], [0, 0, 0, 1, 3299, 143, 5, 2, 1, 6, 82, 16, 4, 147], [7, 2, 0, 1, 136, 1684, 1, 3, 18, 18, 127, 8, 2, 30], [0, 0, 0, 0, 38, 12, 3, 0, 0, 0, 8, 0, 0, 0], [0, 0, 0, 0, 22, 12, 0, 115, 0, 0, 7, 1, 0, 4], [1, 0, 0, 0, 2, 29, 0, 0, 107, 1, 6, 0, 0, 1], [3, 0, 0, 0, 18, 23, 0, 1, 0, 699, 4, 1, 0, 87], [1, 0, 0, 4, 60, 133, 1, 0, 3, 1, 1543, 15, 1, 10], [7, 2, 0, 3, 37, 38, 0, 2, 0, 4, 105, 18, 0, 6], [0, 0, 0, 0, 40, 11, 0, 0, 0, 4, 1, 0, 73, 13], [82, 2, 1, 0, 145, 62, 1, 5, 0, 46, 15, 5, 1, 1638]]
