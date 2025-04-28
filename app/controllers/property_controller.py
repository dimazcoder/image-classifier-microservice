import asyncio
import json
import logging

from app.repositories.image_repository import ImageRepository
from app.schemas.property_schema import PropertySchema, PropertyImagesSchema
from app.services.property_image_service import PropertyImageService
from app.services.queue_service import QueueService


class PropertyController:
    def __init__(self):
        self.image_repository = ImageRepository()
        self.property_image_service = PropertyImageService()
        self.queue_service = QueueService()

    async def extract_images_from_property_om(self, property_data: PropertySchema):
        logging.info(f"Start processing property {property_data}")

        # if OM does not contain PDFs, sending empty result
        if not property_data.pdfs or not len(property_data.pdfs):
            logging.info(f"PDF not found, sending empty list...")
            return await self.send_property_om_images(
                property_data, []
            )

        # searches for previously extracted OM images
        existing_images = await self.image_repository.get_images(
            property_data.property_id
        )
        if existing_images:
            logging.info(f"Property cached images found, sending {len(existing_images)} images...")
            return await self.send_property_om_images(
                property_data, existing_images
            )

        # extracts images from PDF and splits the result into bundles
        bundles = await self.property_image_service.extract_images(
            property_data,
            bundle_size=10
        )

        # sends empty result if nothing is found in the PDF
        if not bundles:
            return await self.send_property_om_images(
                property_data, []
            )

        await self.process_property_om_image_bundles(
            bundles=bundles, property_data=property_data
        )

        # # 20240705, Dima: commented with implementing queueless
        # # processes the first bundle
        # property_images = PropertyImagesSchema.from_params(
        #     property_data=property_data,
        #     images=bundles[0],
        # )
        # await self.process_property_om_images(
        #     property_images
        # )
        #
        # # schedules processing of other bundles
        # await self.schedule_property_om_image_processing(
        #     property_data,
        #     bundles[1:]
        # )

    async def process_property_om_image_bundles(self, bundles: list[list[str]], property_data: PropertySchema):
        tasks = []
        for bundle in bundles:
            property_images = PropertyImagesSchema.from_params(
                property_data=property_data,
                images=bundle,
            )
            task = self.process_property_om_images(property_images)
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def process_property_om_images(self, property_images: PropertyImagesSchema):
        logging.info(f"Start image processing for property_id: {property_images.property_data.property_id}")
        property_data = property_images.property_data
        image_urls = await self.property_image_service.process_images(
            property_images
        )

        await self.send_property_om_images(
            property_data, image_urls
        )

        await self.image_repository.add_images(
            property_data.property_id,
            image_urls
        )

    # # 20240705, Dima: commented with implementing queueless
    # async def schedule_property_om_image_processing(self, property_data: PropertySchema, bundles: list[list[str]]):
    #     logging.info(f"Start scheduling the image processing property_id: {property_data.property_id} bundles {len(bundles)}")
    #     for bundle in bundles:
    #         property_images = PropertyImagesSchema.from_params(
    #             property_data=property_data,
    #             images=bundle,
    #         )
    #         await self.queue_service.send_direct_message(
    #             'image_classifying_tasks',
    #             property_images.json()
    #         )

    async def send_property_om_images(self, property_data: PropertySchema, image_urls):
        message = {
            "user_id": property_data.user_id,
            "property_id": property_data.property_id,
            "image_urls": image_urls,
        }

        await self.queue_service.send_message(
            'property_images_extraction_ready',
            json.dumps(message)
        )

    async def get_property_om_images(self, property_id: str):
        existing_images = await self.image_repository.get_images(
            property_id
        )

        return existing_images if existing_images else []

