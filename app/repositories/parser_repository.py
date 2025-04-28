from typing import List, Optional
from app.infrastructure.adapters.mongo_adapter import MongoAdapter

class ParserRepository:
    def __init__(self):
        self.adapter = MongoAdapter("parser_attempts")

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
            await adapter.insert_document({
                "property_id": property_id,
                "image_urls": links
            })
