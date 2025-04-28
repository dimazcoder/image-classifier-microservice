import logging
import os
import aiofiles
from typing import List

from app.core.config import config
from app.core.my.classifiers.real_estate_image_classifier import RealEstateImageClassifier
from app.core.my.extractors.pdf_image_extractor import PdfImageExtractor


class GalleryService:
    async def get_images_from_pdf(self, pdf_file_path: str) -> List[str]:
        pdf_file_name = os.path.basename(pdf_file_path)
        pdf_folder_name = ".".join(pdf_file_name.split('.')[:-1])

        pdf_images_directory_path = os.path.join(config.pdf_images_path, pdf_folder_name)
        os.makedirs(pdf_images_directory_path, exist_ok=True)

        extractor = PdfImageExtractor()
        image_list = await extractor.process_file(
            pdf_file_path, pdf_images_directory_path
        )

        return image_list

    async def classify_images(self, image_paths: List[str]) -> list[str]:
        logging.info("Image Classification...")
        valid_images = []

        # supervised dataset folders
        real_estate_images, invalid_images = self.get_classifier_path()

        classifier = RealEstateImageClassifier()
        for file_path in image_paths:
            real_estate_image = classifier.is_real_estate_image(
                file_path
            )

            if real_estate_image:
                valid_images.append(file_path)
                destination_file_path = real_estate_images
            else:
                destination_file_path = invalid_images

            # copies image to classifier directory to use in further training
            await self.copy_file(file_path, destination_file_path)

        return valid_images

    async def copy_file(self, src: str, dest: str) -> None:
        file_name = os.path.basename(src)
        dest = os.path.join(dest, file_name)
        async with aiofiles.open(src, 'rb') as fsrc:
            async with aiofiles.open(dest, 'wb') as fdest:
                await fdest.write(await fsrc.read())

    def get_classifier_path(self):
        dataset_path = os.path.join(config.classifier_path, 'real_estate_images', 'work_dataset')
        os.makedirs(dataset_path, exist_ok=True)
        real_estate_images = os.path.join(dataset_path, 'real_estate')
        os.makedirs(real_estate_images, exist_ok=True)
        invalid_images = os.path.join(dataset_path, 'invalid')
        os.makedirs(invalid_images, exist_ok=True)

        return real_estate_images, invalid_images
