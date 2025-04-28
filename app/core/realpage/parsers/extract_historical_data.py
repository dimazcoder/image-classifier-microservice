import fitz  # PyMuPDF
import csv
import re
import os


def extract_text_from_page(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    text = page.get_text("text")
    return text


def clean_line(line):
    line = re.sub(r'[^a-zA-Z0-9\s/]', '', line)
    line = re.sub(r'\s+', ' ', line)
    line = re.sub(r'\s*/\s*', '/', line)
    return line.lower().strip()


def find_full_block_keyword(buffer, block_keyword):
    cleaned_keyword = clean_line(block_keyword)

    for i in range(len(buffer)):
        combined_line = ' '.join(buffer[i:]).strip()
        if clean_line(combined_line) == cleaned_keyword:
            return True
    return False


def process_block(text, output_dir, block_keyword, headers, quarter_regex, row_length):
    lines = iter(text.split('\n'))
    block_data = []
    buffer = []

    for line in lines:
        cleaned_line = clean_line(line.strip())
        buffer.append(cleaned_line)
        if len(buffer) > 4:
            buffer.pop(0)

        if find_full_block_keyword(buffer, block_keyword):
            buffer = []  # Clear buffer after finding the keyword
            try:
                while True:
                    data_row = [next(lines).strip() for _ in range(row_length)]
                    if quarter_regex.match(data_row[0]):
                        block_data.append(data_row)
                    else:
                        break
            except StopIteration:
                break

    if block_data:
        output_path = os.path.join(output_dir, f"{block_keyword.replace(' ', '_').replace('/', '_')}.csv")
        save_to_csv(block_data, output_path, headers)
        print(f"Data saved to {output_path}", flush=True)

    return block_data


def save_to_csv(data, output_path, headers):
    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)


def find_historical_data_page(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        text = extract_text_from_page(pdf_path, page_num)
        if "HISTORICAL DATA" in text:
            return page_num
    return None


def process_pdf(pdf_path, output_dir):
    block_configs = [
        {
            'block_id': 'occupancy',
            'block_keyword': 'Occupancy',
            'headers': ['Period', 'Total', 'Eff', '1 BR', '2 BR', '3 BR', '2000+', '1990s', '1980s', '1970s',
                        'Pre-1970', 'Low-Rise', 'Mid-Rise', 'High-Rise'],
            'row_length': 14
        },
        {
            'block_id': 'monthly_rent',
            'block_keyword': 'Monthly Rent',
            'headers': ['Period', 'Total', 'Eff', '1 BR', '2 BR', '3 BR', '2000+', '1990s', '1980s', '1970s',
                        'Pre-1970', 'Low-Rise', 'Mid-Rise', 'High-Rise'],
            'row_length': 14
        },
        {
            'block_id': 'rent_per_sqft',
            'block_keyword': 'Rent Per Square Foot',
            'headers': ['Period', 'Total', 'Eff', '1 BR', '2 BR', '3 BR', '2000+', '1990s', '1980s', '1970s',
                        'Pre-1970', 'Low-Rise', 'Mid-Rise', 'High-Rise'],
            'row_length': 14
        },
        {
            'block_id': 'annual_rent_change',
            'block_keyword': 'Annual Rent Change',
            'headers': ['Period', 'Total', 'Eff', '1 BR', '2 BR', '3 BR', '2000+', '1990s', '1980s', '1970s',
                        'Pre-1970', 'Low-Rise', 'Mid-Rise', 'High-Rise'],
            'row_length': 14
        },
        {
            'block_id': 'annual_revenue_change',
            'block_keyword': 'Annual Revenue Change',
            'headers': ['Period', 'Total', 'Eff', '1 BR', '2 BR', '3 BR', '2000+', '1990s', '1980s', '1970s',
                        'Pre-1970', 'Low-Rise', 'Mid-Rise', 'High-Rise'],
            'row_length': 14
        },
        {
            'block_id': 'supply_demand',
            'block_keyword': 'Supply/Demand',
            'headers': ['Period', 'Supply Quarterly', 'Supply Annual', 'Demand Quarterly', 'Demand Annual',
                        'Inventory Change Quarterly', 'Inventory Change Annual'],
            'row_length': 7
        },
        {
            'block_id': 'sample_existing_units',
            'block_keyword': 'Sample/Existing Units',
            'headers': ['Period', 'Existing Units', 'Sampled Units', 'Percent Sampled'],
            'row_length': 4
        }
    ]

    quarter_regex = re.compile(r'^\dQ \d{2}$')

    historical_data_page = find_historical_data_page(pdf_path)
    historical_data = {
        'occupancy': [],
        'monthly_rent': [],
        'rent_per_sqft': [],
        'annual_rent_change': [],
        'annual_revenue_change': [],
        'supply_demand': [],
        'sample_existing_units': []
    }
    if historical_data_page is not None:

        text = extract_text_from_page(pdf_path, historical_data_page)

        for config in block_configs:
            historical_data[config['block_id']] = process_block(text, output_dir, config['block_keyword'], config['headers'], quarter_regex,
                          config['row_length'])
    else:
        print("HISTORICAL DATA page not found", flush=True)
    return historical_data


def extract_historical_data(path, submarket_key):
    pdf_path = f'{path}/{submarket_key}.pdf'
    return process_pdf(pdf_path, path)
