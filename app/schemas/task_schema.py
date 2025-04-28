from typing import List
from pydantic import BaseModel


class TaskSchema(BaseModel):
    task: str
    payload: dict
