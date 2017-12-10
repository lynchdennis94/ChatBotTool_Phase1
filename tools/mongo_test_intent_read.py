from pymongo import MongoClient
from pprint import pprint

client = MongoClient(port=27017)
db=client.chatbot

result_list = db.intent.find({'intent' : 'gre'})
for result in result_list:
	print("")
	pprint(result)
	print("")
