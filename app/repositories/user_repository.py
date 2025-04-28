from typing import Dict, Optional
from app.infrastructure.adapters.mongo_async_adapter import MongoAsyncAdapter
from app.schemas.user_schema import UserSchema


class UserRepository:
    def __init__(self):
        self.adapter = MongoAsyncAdapter("users")

    async def get_user(self, user_id) -> Optional[UserSchema]:
        async with self.adapter as adapter:
            # we also need to check here if user is active
            doc = await adapter.find_document({
                "_id": user_id
            })

        if doc:
            return UserSchema(**doc)
        return None
