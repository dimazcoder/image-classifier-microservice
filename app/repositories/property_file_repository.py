import os

from app.core.config import config
from app.infrastructure.adapters.s3_async_adapter import S3AsyncAdapter
from app.infrastructure.adapters.gcp_adapter import GCPAdapter
from app.schemas.pdf_schema import PdfSchema
from app.schemas.property_schema import PropertySchema


class PropertyFileRepository:
    def __init__(self):
        self.adapter = GCPAdapter()

    def get_local_dir(self, property: PropertySchema) -> str:
        path = os.path.join(
            config.downloads_path, property.user_id, property.property_id
        )
        os.makedirs(path, exist_ok=True)
        return path

    async def download_pdf(self, pdf: PdfSchema, path: str) -> str:
        local_file_path = await self.adapter.download_file(
            pdf.cloud_bucket, path
        )
        return local_file_path

    async def upload_image(self, local_path: str, property_id: str) -> str:
        # file_name = local_path.split('/')[-1]
        # cloud_path = os.path.join(property_id, file_name)
        cloud_path = self.prep_path(
            local_path, property_id
        )
        url = await self.adapter.upload_file(
            config.s3_image_bucket, local_path, cloud_path
        )
        return url

    def get_image_url(self, local_path: str, property_id: str) -> str:
        cloud_path = self.prep_path(
            local_path, property_id
        )
        return self.adapter.get_url(
            config.s3_image_bucket, cloud_path
        )

    def prep_path(self, file_path: str, folder: str) -> str:
        file_name = file_path.split('/')[-1]
        return os.path.join(
            folder, file_name
        )

