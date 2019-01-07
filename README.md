# python 3
pip install -r requirements.txt

python main.py

# curling
 curl -i -X POST localhost:8181/api/v1/transactions -H "Content-Type: text/xml" --data-binary "@./data/transactions.json"
# heavywater
