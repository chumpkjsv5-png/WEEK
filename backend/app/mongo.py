import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection

load_dotenv()

_client = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=3000)


def get_content_collection() -> Collection:
    return _client.get_default_database()["article_contents"]