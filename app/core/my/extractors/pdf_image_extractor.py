import io
import logging
import os
import shutil
import traceback
from enum import Enum
from typing import Callable, List
import aiofiles

import fitz
from PIL import Image

from app.core.config import config
from app.utils.helpers import gen_kebab_name, prep_hash


class ImageSize(Enum):
    HEIGHT = 150
    WIDTH = 150


# function must take two arguments: page_number, image_index
FileNameFunction = Callable[[int, int], str]


class PdfImageExtractor:
    def __init__(self):
        self.min_image_height = ImageSize.HEIGHT.value
        self.min_image_width = ImageSize.WIDTH.value
        self.default_image_directory_path = config.pdf_images_path

    async def process_file(self, file_path, image_directory_path=None, file_name_func: FileNameFunction = None) -> List[str]:
        if not file_path.endswith(".pdf"):
            raise Exception("PDF file extension must be '.pdf'")

        if file_name_func is None:
            file_name_func = self.gen_file_name

        if image_directory_path is None:
            image_directory_path = self.default_image_directory_path

        pdf_document = fitz.open(file_path)
        seen_hashes = set()
        created_image_paths = []

        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            images = page.get_images(full=True)
            for img_index, img in enumerate(images):
                try:
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_hash = prep_hash(image_bytes)

                    if image_hash in seen_hashes:
                        logging.warning(f"Duplicate image detected on page {page_number}, image {img_index}. Skipping...")
                        continue

                    pil_image = Image.open(io.BytesIO(image_bytes))
                    if pil_image.mode in ('RGBA', 'P'):
                        pil_image = convert_rgba_to_rgb(pil_image)

                    if pil_image.width > self.min_image_width and pil_image.height > self.min_image_height:
                        img_name = file_name_func(page_number, img_index)
                        img_path = os.path.join(image_directory_path, f'{img_name}.jpg')

                        async with aiofiles.open(img_path, 'wb') as img_file:
                            pil_image.save(img_file, format='JPEG')

                        created_image_paths.append(img_path)
                        seen_hashes.add(image_hash)
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    logging.error(f"Exception while processing image {img_index} on page {page_number}: {traceback_str}")

        return created_image_paths

    def process_directory(self, source_directory_path, image_directory_path, processed_path=None) -> bool:
        # if at least one file from the directory has been processed, the directory will be considered processed
        directory_processed = False
        for filename in os.listdir(source_directory_path):
            if filename.endswith(".pdf"):
                logging.info(f'Processing {filename}')
                file_path = os.path.join(source_directory_path, filename)
                self.process_file(
                    file_path, image_directory_path
                )
                if processed_path:
                    shutil.move(file_path, processed_path)
                directory_processed = True
        return directory_processed

    def gen_file_name(self, page_number, image_index) -> str:
        return gen_kebab_name()

def convert_rgba_to_rgb(image: Image) -> Image:
    return image.convert('RGB')