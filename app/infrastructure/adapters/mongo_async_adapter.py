import motor.motor_asyncio
from app.core.config import config

class MongoAsyncAdapter:
    def __init__(self, collection_name=None, database_name=None):
        self.database_name = database_name if database_name is not None else config.default_db
        self.collection_name = collection_name
        self.client = None

    async def connect(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(config.mongo_uri)

    async def __aenter__(self):
        await self.connect()
        self.db = self.client[self.database_name]
        self.collection = self.db[self.collection_name]
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.client.close()

    async def find_document(self, query):
        return await self.collection.find_one(query)

    async def find_all_documents(self, query):
        cursor = self.collection.find(query)
        return [doc async for doc in cursor]

    async def document_exist(self, query):
        return await self.collection.count_documents(query, limit=1)

    async def insert_document(self, doc):
        res = await self.collection.insert_one(doc)
        return res.inserted_id

    async def update_one(self, filter_criteria, update_operation, **kwargs):
        result = await self.collection.update_one(filter_criteria, update_operation, **kwargs)
        return result

    async def update_many(self, filter_criteria, update_operation):
        result = await self.collection.update_many(filter_criteria, update_operation)
        return result

    async def delete_first(self, query):
        result = await self.collection.find_one_and_delete(query)
        return result

    async def delete_as_many(self, query):
        result = await self.collection.delete_many(query)
        return result

    async def get_all(self):
        cursor = self.collection.find({})
        return [doc async for doc in cursor]

    async def remove_all(self):
        result = await self.collection.delete_many({})
        return result
