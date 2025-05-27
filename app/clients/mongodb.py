# 실제 MongoDB 클라이언트에서 import
from dotenv import load_dotenv
from pymongo import MongoClient


#MONGO_URL = "mongodb://localhost:27017"
MONGO_URL = "mongodb://54.180.4.224:27017"
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["ai_platform"]
