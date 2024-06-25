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
        # value = value.replace(',', '')
        
        # Check if the value is a date in MM/DD/YYYY format
        date_pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        if date_pattern.match(value):
            try:
                return datetime.strptime(value, '%m/%d/%Y').date()
            except ValueError:
                pass  # If date parsing fails, proceed to other checks
        return value

# Converts each line in a PDF page into a list and removes spaces. This allows us to iterate based on the patterns of the data
def get_lines_without_spaces(page, cutoff):
    messy_lines = page.split('\n')
    clean_lines = []
    for line in messy_lines:
        clean_lines.append(list(filter(None, line.split(' '))))
    detail = clean_lines[cutoff:]
    headers = clean_lines[:cutoff]
    return(headers, detail)

# Extracts data from page, separates the header from the rest of the data per page
def get_all_page_lines(pages, cutoff):
    headers = []
    lines = []
    for page in pages:
        page_text = page.extract_text()
        if '< CONTINUED >' in page_text:
            headers, detail = get_lines_without_spaces(page_text, cutoff)
            lines.extend(detail)
    return(headers, lines)

def get_next_value(lst, previous_value):
    if previous_value in lst:
        index = lst.index(previous_value)
        if index < len(lst) - 1:
            return lst[index + 1]
        else:
            return None
    else:
        return None
    
def remove_empty_lists(list_of_lists):
    return [sublist for sublist in list_of_lists if sublist 
            and 'PREFERRED' not in sublist
            and 'BLUE' not in sublist]

def custom_serializer(obj):
    if isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

# Handling payer info by extracting from headers
def get_payer_details(headers):
    payer_dict = {}
    # payer_detail_keys = ['PAYEE ID', 'NPI ID', 'CHECK NUMBER', 'ISSUE DATE']
    for itr, header in enumerate(headers):
        find_keys = ["PAYROLL:","PAYEE:","TAX:","PROVIDER:"]
        for find_key in find_keys:
            if find_key in header:
                payer_dict.update({find_key.split(":")[0]: header[-1]})
    return payer_dict

def insert_none_and_combine_in_range(lst, start, end):
    result = lst[:start]
    temp = []

    def add_temp_to_result():
        if temp:
            result.append(', '.join(temp))
            temp.clear()

    for i in range(start, end):
        if '.' in lst[i]:
            add_temp_to_result()
            if result and '.' in result[-1]:
                result.append(None)
            result.append(lst[i])
        else:
            temp.append(lst[i])
    
    # Add any remaining values in temp to result
    add_temp_to_result()

    result.extend(lst[end:])
    return result