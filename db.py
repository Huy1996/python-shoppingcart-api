from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient

load_dotenv(find_dotenv())

connection_string = os.environ.get("MONGO_URL")
mongo = MongoClient(connection_string)
db = mongo.shopping_cart