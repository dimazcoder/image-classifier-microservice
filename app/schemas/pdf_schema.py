from typing import List
from pydantic import BaseModel


class PdfSchema(BaseModel):
    s3_link: str
    cloud_bucket: dict
    file_name: str
    file_size: str
    file_ext: str
