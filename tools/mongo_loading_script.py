import json
from pymongo import MongoClient


client = MongoClient(port=27017)
db=client.chatbot

with open('OMSCSLexJson1.json') as input_file:
    data = json.load(input_file)

# Clean out old loaded info in collection
db.intent.remove()

for intent_key in data:
    intent_item = {
                    'intent' : intent_key,
                    'response' : data[intent_key]['response']
                }
    db.intent.insert_one(intent_item)

