from operator import itemgetter
import json
from IPython.display import display, Markdown, Image
from PyPDF2 import PdfReader
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import os
import pandas as pd

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

# Converts each line in a PDF page into a list and removes spaces. This allows us to iterate based on the patterns of the data
def get_lines_without_spaces(page):
    messy_lines = page.split('\n')
    clean_lines = []
    for line in messy_lines:
        clean_lines.append(list(filter(None, line.split(' '))))
    detail = clean_lines[10:]
    headers = clean_lines[:10]
    return(headers, detail)

# Extracts data from page, separates the header from the rest of the data per page
def get_all_page_lines_by_claim_header_type(pages, claim_type):
    headers = []
    lines = []
    for page in pages:
        page_text = page.extract_text()
        if claim_type in page_text:
            headers, detail = get_lines_without_spaces(page_text)
            lines.extend(detail)
    return(headers, lines)

# Util function used to get the indicies of each table based on the appearance of "NAME:"
# See below for use case.
def get_next_value(lst, previous_value):
    if previous_value in lst:
        index = lst.index(previous_value)
        if index < len(lst) - 1:
            return lst[index + 1]
        else:
            return None
    else:
        return None

# Handling payer info by extracting from headers
def get_payer_details(headers):
    payer_dict = {}
    payer_detail_keys = ['PAYEE ID', 'NPI ID', 'CHECK NUMBER', 'ISSUE DATE']
    for itr, header in enumerate(headers):
        if 'PAYEE' in header:
            payer_dict = {payer_detail_keys[0]: parse_value(headers[itr][-1])}
            payer_dict.update({payer_detail_keys[1]: headers[itr + 1][-1]})
            payer_dict.update({payer_detail_keys[2]: headers[itr + 2][-1]})
            payer_dict.update({payer_detail_keys[3]: headers[itr + 3][-1]})
    return payer_dict


def remove_claim_header_rows(data, column_header):
    return [row for row in data if row[0] != column_header]


def check_claim_transformations(temp_lines, claims_list, column_header_check):
    temp_lines_len_check = len(remove_claim_header_rows(temp_lines, column_header_check))
    final_claim_lines_len_check = len(claims_list)
    if temp_lines_len_check != final_claim_lines_len_check:
        print(temp_lines_len_check)
        print(temp_lines)
        print(final_claim_lines_len_check)
        print(claims_list)
        print()

def pad_list_to_length_in_place(input_list, target_length):
    current_length = len(input_list)
    if current_length < target_length:
        input_list.extend([None] * (target_length - current_length))