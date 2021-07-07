import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv('./.env')
MONGO_URL = os.getenv('MONGO_URL')

cluster = MongoClient(MONGO_URL)
db = cluster['dusk-bank']
collection = db['bank']

test = {'_id':0, 'name':'Test'}
collection.insert_one(test)


# mongodb+srv://Turtle:<password>@cluster0.kmnpl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority