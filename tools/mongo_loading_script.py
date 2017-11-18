import json
from pymongo import MongoClient


client = MongoClient(port=27017)
db=client.chatbot

with open('OMSCSLexJson2.json') as input_file:
    data = json.load(input_file)

# Clean out old loaded info in collection
db.intent.remove()

for intent_key in data:
    response_list = data[intent_key]['response']
    for response in response_list:
        intent_item = {
                        'intent' : intent_key,
                        'response' : response,
                        'weight' : 15.0
                    }
        db.intent.insert(intent_item)

