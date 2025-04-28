import fitz  # PyMuPDF
import re
import os


def get_text_with_previous(doc, page_num):
    """Returns the combined text of the given page and the previous page."""
    text = doc.load_page(page_num).get_text()
    if page_num > 0:
        text = doc.load_page(page_num - 1).get_text() + "\n" + text
    return text


def split_pdf_by_submarkets(submarkets, market_directory, file):
    print(submarkets, flush=True)

    os.makedirs(market_directory, exist_ok=True)

    doc = fitz.open(file)
    market_pdf_path = os.path.join(market_directory, 'market.pdf')
    print(f"Saving market PDF to {market_pdf_path}", flush=True)
    doc.save(market_pdf_path)

    for submarket in submarkets:
        submarket_directory = os.path.join(market_directory, str(submarket['submarket_key']))
        os.makedirs(submarket_directory, exist_ok=True)
        key = submarket['submarket_key']
        name = submarket['name']
        submarket_pages = []

        # Compile regex to match "key" followed by one or more spaces and then "name"
        pattern = re.compile(rf"{key}\s+{re.escape(name)}")

        quarters = [
            '2Q 2023', '3Q 2023', '4Q 2023',
            '1Q 2024', '2Q 2024', '3Q 2024', '4Q 2024'
        ]

        def find_start_page(doc):
            for page_num in range(len(doc)):
                # Get the text of the current page
                text = doc.load_page(page_num).get_text()
                # Check if the page contains the submarket header
                if ('Submarket Overview' in text
                        and any(q in text for q in quarters)
                        and pattern.search(text)
                        and 'SNAPSHOT' in text):
                    return page_num
            return -1

        # First attempt to find the start page
        start_page_num = find_start_page(doc)

        # If not found, try to find with combined text from previous page
        if start_page_num == -1:
            for page_num in range(len(doc)):
                combined_text = get_text_with_previous(doc, page_num)
                if ('Submarket Overview' in combined_text
                        and any(q in combined_text for q in quarters)
                        and pattern.search(combined_text)
                        and 'SNAPSHOT' in combined_text):
                    start_page_num = page_num
                    break

        if start_page_num != -1:
            print(f"Found {name} starting on page {start_page_num}", flush=True)
        else:
            print(f"Failed to find the start page for {name}", flush=True)
            continue

        # Iterate to find the end page
        for page_num in range(start_page_num, len(doc)):
            text = doc.load_page(page_num).get_text()
            # Check if the page contains "HISTORICAL DATA"
            if 'HISTORICAL DATA' in text and name in text:
                print(f"Found HISTORICAL DATA on page {page_num}", flush=True)
                end_page_num = page_num
                break
        else:
            end_page_num = -1

        # Extract pages from start_page_num to end_page_num
        if start_page_num != -1 and end_page_num != -1:
            submarket_pages = [doc.load_page(i) for i in range(start_page_num, end_page_num + 1)]

            # Save the extracted pages to a new PDF
            if submarket_pages:
                new_doc = fitz.open()
                for page in submarket_pages:
                    new_doc.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
                submarket_pdf_path = os.path.join(submarket_directory, f'{key}.pdf')
                new_doc.save(submarket_pdf_path)
                new_doc.close()
        else:
            print(f"Failed to find the end page for {name}", flush=True)
