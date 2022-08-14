from pymongo import MongoClient
from config import MONGO_URL

mongo = MongoClient(MONGO_URL)
db = mongo.shopping_cart