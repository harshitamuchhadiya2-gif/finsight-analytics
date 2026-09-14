from pymongo import MongoClient
from app.core.config import MONGODB_URL, MONGODB_DB

client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[MONGODB_DB]

def get_db():
    return db
