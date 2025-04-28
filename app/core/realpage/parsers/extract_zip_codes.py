import fitz  # PyMuPDF
import re


def extract_text_from_page(pdf_path, page_num):
    """Extracts text from a specific page in the PDF."""
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    return page.get_text()


def find_zip_code_page_text(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        text = extract_text_from_page(pdf_path, page_num)
        if "ZIP Code List" in text:
            return text
    return None


def find_zip_codes(text):
    zip_codes = []

    # Find the position of "ZIP Code List" in the text
    zip_code_list_position = text.find("ZIP Code List")

    if zip_code_list_position != -1:
        # Extract the part of the text after "ZIP Code List"
        text_after_zip_code_list = text[zip_code_list_position + len("ZIP Code List:"):]

        # Find all 5-6 digit numbers followed by a comma or end of text
        matches = re.findall(r'\b\d{5,6}\b', text_after_zip_code_list)
        zip_codes.extend(matches)

    return zip_codes


def format_zip_codes(zip_codes, submarket, market):
    result = []
    for zip_code in zip_codes:
        result.append({
            "zipcode": zip_code,
            "state": market['state'],
            "market": market['market'],
            "submarket": submarket['name']
        })
    return result


def extract_zip_codes(path, submarket, market):
    submarket_key = submarket['submarket_key']
    pdf_path = f'{path}/{submarket_key}.pdf'
    text = find_zip_code_page_text(pdf_path)
    if text is None:
        return []
    zip_codes = find_zip_codes(text)

    return format_zip_codes(zip_codes, submarket, market)
