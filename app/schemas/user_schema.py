from pydantic import BaseModel


class UserSchema(BaseModel):
    _id: str
    first_name: dict
    last_name: str
