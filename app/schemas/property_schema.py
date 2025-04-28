from typing import List
from pydantic import BaseModel

from app.schemas.pdf_schema import PdfSchema


class PropertySchema(BaseModel):
    user_id: str
    property_id: str
    property_name: str
    pdfs: List[PdfSchema]
    excels: List[dict]
    images: List[dict]

class PropertyImagesSchema(BaseModel):
    property_data: PropertySchema
    images: List[str]

    @classmethod
    def from_params(cls, property_data: PropertySchema, images: list[str]) -> 'PropertyImagesSchema':
        return cls(property_data=property_data, images=images)

