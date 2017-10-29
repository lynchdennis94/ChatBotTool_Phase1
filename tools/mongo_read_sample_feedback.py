from pymongo import MongoClient
from pprint import pprint

client = MongoClient(port=27017)
db=client.chatbot

result = db.feedback.find_one({'intent' : 'gre'})
pprint(result)
