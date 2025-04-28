import asyncio
import logging
import os
from typing import List

from app.repositories.property_file_repository import PropertyFileRepository
from app.schemas.property_schema import PropertySchema, PropertyImagesSchema
from app.services.gallery_service import GalleryService
from app.utils.helpers import chunk_list


class PropertyImageService:
    def __init__(self) -> None:
        self.file_repository = PropertyFileRepository()
        self.gallery_service = GalleryService()

    async def extract_images(self, property_data: PropertySchema, bundle_size=None) -> List[List[str]]:
        download_path = self.file_repository.get_local_dir(property_data)
        extracted_image_paths = []

        for pdf in property_data.pdfs:
            pdf_file_path = await self.file_repository.download_pdf(pdf, download_path)
            image_paths = await self.gallery_service.get_images_from_pdf(
                pdf_file_path
            )
            extracted_image_paths.extend(image_paths)

        if bundle_size:
            bundled_image_paths = chunk_list(extracted_image_paths, bundle_size)
        else:
            bundled_image_paths = [extracted_image_paths]

        return bundled_image_paths

    async def process_images(self, property_images: PropertyImagesSchema):
        property_data = property_images.property_data
        image_paths = property_images.images

        valid_paths = await self.gallery_service.classify_images(
            image_paths
        )

        image_urls = []
        for path in valid_paths:
            url = self.file_repository.get_image_url(
                path,
                property_data.property_id
            )
            image_urls.append(url)

        # Run the upload and cleanup in a separate thread
        await self.upload_images_and_cleanup(property_data, valid_paths)

        return image_urls

    async def upload_images_and_cleanup(self, property_data: PropertySchema, valid_paths: List[str]):
        upload_tasks = [self.file_repository.upload_image(path, property_data.property_id) for path in valid_paths]
        await asyncio.gather(*upload_tasks)

        cleanup_tasks = [self.delete_file(path) for path in valid_paths]
        await asyncio.gather(*cleanup_tasks)

    async def delete_file(self, path: str):
        try:
            os.remove(path)
        except OSError as e:
            logging.error(f"Error deleting file {path}: {e}")