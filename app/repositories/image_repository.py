from typing import List, Optional
from app.infrastructure.adapters.mongo_async_adapter import MongoAsyncAdapter


class ImageRepository:
    def __init__(self):
        self.adapter = MongoAsyncAdapter("om-images")

    async def property_exist(self, property_id) -> bool:
        async with self.adapter as adapter:
            return await adapter.document_exist({
                "property_id": property_id
            })

    async def get_images(self, property_id) -> Optional[List[str]]:
        async with self.adapter as adapter:
            doc = await adapter.find_document({
                "property_id": property_id
            })

        if doc is None or "image_urls" not in doc:
            return None

        return doc["image_urls"]

    async def add_images(self, property_id, links) -> None:
        async with self.adapter as adapter:
            await adapter.update_one(
                {"property_id": property_id},
                {'$addToSet': {'image_urls': {'$each': links}}},
                upsert=True
            )
