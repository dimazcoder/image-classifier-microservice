import pymongo
from app.core.config import config

class MongoAdapter:
    def __init__(self, collection_name=None, database_name=None):
        self.database_name = database_name if database_name is not None else config.default_db
        self.collection_name = collection_name
        self.client = None

    def connect(self):
        self.client = pymongo.MongoClient(config.mongo_uri)

    def __enter__(self):
        self.connect()
        self.db = self.client[self.database_name]
        self.collection = self.db[self.collection_name]
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def find_document(self, query):
        return self.collection.find_one(query)

    def find_all_documents(self, query=None):
        cursor = self.collection.find(query)
        return [doc for doc in cursor]

    def document_exist(self, query):
        return self.collection.count_documents(query, limit=1)

    def insert_document(self, doc):
        res = self.collection.insert_one(doc)
        return res.inserted_id

    def update_one(self, filter_criteria, update_operation, **kwargs):
        result = self.collection.update_one(filter_criteria, update_operation, **kwargs)
        return result

    def update_many(self, filter_criteria, update_operation):
        result = self.collection.update_many(filter_criteria, update_operation)
        return result

    def delete_first(self, query):
        result = self.collection.find_one_and_delete(query)
        return result

    def delete_as_many(self, query):
        result = self.collection.delete_many(query)
        return result

    def get_all(self):
        cursor = self.collection.find({})
        return [doc for doc in cursor]

    def remove_all(self):
        result = self.collection.delete_many({})
        return result

    def aggregate(self, filter_criteria):
        result = self.collection.aggregate(filter_criteria)
        return result

    def create_index(self, query):
        self.collection.create_index(query)
