import requests
import json
import pdb

"""
curl -X POST https://sandbox.plaid.com/institutions/get \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": String,
    "secret":String,
    "count": Number,
    "offset": Number
  }'
"""

VERSION = 1
filename = '/Users/xerox/code/harvest/harvest-compute/data/institutions_v' + str(VERSION) + ".json"

client_id = "5a5d17008d923955ed7dd943"
secret = "a18af1ec7f968c0a4ba410ddcea887"
headers = {'Content-type': 'application/json'}
req = requests.post("https://sandbox.plaid.com/institutions/get", 
                    json={'client_id': client_id, 'secret': secret, 'count': 500, 'offset': 0},
                    headers=headers
                  )

data = json.loads(req.text)
total = data['total']

batch_size = 500
offset = 0
institutions = []
while (offset < total):
    req = requests.post("https://sandbox.plaid.com/institutions/get", 
                    json={
                        'client_id': client_id, 
                        'secret': secret, 
                        'count': batch_size, 
                        'offset': offset
                    },
                    headers=headers
                  )
    offset = offset
    if (req.status_code != 200):
        raise Exception("received non 200 status")
    data = json.loads(req.text)
    institutions = institutions + data['institutions']
    print("offset:" + str(offset))
    offset = offset + batch_size

print("total:" + str(total))
print("total size of institutions:" + str(len(institutions)))
with open(filename, 'w') as outfile:
    json.dump(institutions, outfile)
print("wrote to: " + filename)


