from .packages import *
def parse_value(value):
    if value is None or isinstance(value, list):
        return value
    
    if not isinstance(value, list):
        # Handle values enclosed in parentheses
        if value.startswith('(') and value.endswith(')'):
            value = f"-{value[1:-1]}"
        
        # Replace Unicode minus sign with standard minus sign
        value = value.replace('\u2212', '-')

        # Replace Unicode minus sign with standard minus sign
        value = value.replace('\u2019', '-')
        
        # Remove commas
        value = value.replace(',', '')
        
        # Check if the value is a date in MM/DD/YYYY format
        date_pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        if date_pattern.match(value):
            try:
                return datetime.strptime(value, '%m/%d/%Y').date()
            except ValueError:
                pass  # If date parsing fails, proceed to other checks
        return value

def custom_serializer(obj):
    if isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def pad_list_to_length_in_place(input_list, target_length):
    current_length = len(input_list)
    if current_length < target_length:
        input_list.extend([None] * (target_length - current_length))


def split_value(value):
    match = re.match(r'(\d+)([A-Z]\d+)', value)
    if match:
        return match.groups()
    return None

def get_lines_without_spaces(page):
    partition = 16
    messy_lines = page.split('\n')
    clean_lines = []
    for line in messy_lines:
        # print(line)
        clean_lines.append(list(filter(None, line.split(' '))))
    detail = clean_lines[partition:]
    headers = clean_lines[:partition]
    return(headers, detail)

# Extracts data from page, separates the header from the rest of the data per page
def get_all_page_lines_by_claim_header_type(pages):
    headers_total = []
    lines = []
    for page in pages:
        page_text = page.extract_text()
        headers, detail = get_lines_without_spaces(page_text)
        lines.append(detail)
        headers_total.append(headers)
    return(headers_total, lines)