import io
import os
import random
import shutil
import string

import fitz
from PIL import Image

min_width = 150
min_height = 150

def extract_images_from_pdf(file_path, image_directory_path) -> None:
    if not file_path.endswith(".pdf"):
        raise Exception("PDF file extension must be '.pdf'")

    pdf_document = fitz.open(file_path)
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        images = page.get_images(full=True)
        for img_index, img in enumerate(images):
            try:
                image_bytes = pdf_document.extract_image(img[0])
                pil_image = Image.open(io.BytesIO(image_bytes['image']))
                if pil_image.width > min_width and pil_image.height > min_height:
                    img_name = gen_file_name()
                    img_path = os.path.join(image_directory_path, f'{img_name}.jpg')
                    pil_image.save(img_path)
            except Exception as e:
                print(f"Exception while page {img_index} on page {page_number}: {e}")


def process_directory(source_directory_path, image_directory_path, handled_directory_path=None) -> bool:
    handled = False
    for filename in os.listdir(source_directory_path):
        if filename.endswith(".pdf"):
            print(f'Processing {filename}', flush=True)
            file_path = os.path.join(source_directory_path, filename)
            extract_images_from_pdf(
                file_path, image_directory_path
            )
            if handled_directory_path:
                shutil.move(file_path, handled_directory_path)
            handled = True
    return handled


def gen_file_name(block_len=4, n_blocks=3) -> str:
    def generate_random_string(length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    return '-'.join(generate_random_string(block_len) for _ in range(n_blocks))
