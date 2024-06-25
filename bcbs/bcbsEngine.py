import os
import json
from io import BytesIO
import zipfile
import pandas as pd
from PyPDF2 import PdfReader


from .master import *
# Define the keys
demo_keys = ["LOCATION ID", "CLAIM NUMBER", "PATIENT LAST NAME", "PATIENT FIRST INITIAL",
             "ORIGINAL MEMBER ID", "CORRECTED MEMBER ID", "PAT ACCT NO"]

claim_keys = ["SERVICE FROM", "DATES THRU", "PLACE OF SERVICE", "PROC CD 1", "PROC CD 2",
              "STATUS", "CHARGE AMOUNT", "PR REASON CODE", "PR AMOUNT",
              "CO REASON CODE", "CO AMOUNT", "OA REASON CODE", "OA AMOUNT", "PAID AMOUNT"]

claim_total_keys = ["TOTAL CHARGE AMOUNT", "TOTAL PR AMOUNT",
                    "TOTAL CO AMOUNT", "TOTAL OA AMOUNT", "TOTAL PAID AMOUNT"]

def extract_all_data(headers, lines):
    lines = remove_empty_lists(lines)
    divider = "_______________________________________________________________________________________________________________________________________________"
    lines.insert(0, divider)
    positions = [itr for itr, line in enumerate(lines) if divider in line]

    final_dicts = []

    payer_details = get_payer_details(headers)
    final_dicts.append(payer_details)

    for itr in positions:
        st = itr + 1
        en = get_next_value(positions, itr)
        try:
            table = lines[st:en]
            # print(table)
        except:
            table = []

        if table:

            # print(table)
            if 'CONTINUED' not in table[0]:
                demo_data = table[0]
                claim_lines = table[1:]
            elif len(table) > 1:
                demo_data = table[1]
                claim_lines = table[2:]

            
            pat_info_dict = {key: parse_value(value) for key, value in zip(demo_keys, demo_data)}
            claims_list = []
            pat_info_dict['CLAIMS'] = claims_list
            # print(f"DEMO: {demo_data}")

            for _, claim_line in enumerate(claim_lines):
                
                if 'CLAIM' not in claim_line:
                    # print(f"CLAIM {claim_line}")
                    if claim_line[4] is not None and '-' in claim_line[4]:
                        claim_line.insert(4, None)

                    claim_line = insert_none_and_combine_in_range(claim_line, 5, len(claim_line) - 1)
                    
                    temp_claim_obj = {key: parse_value(value) for key, value in zip(claim_keys, claim_line)}
                    claims_list.append(temp_claim_obj)

            if 'CLAIM' in claim_line:
                total_claim_obj = {key: parse_value(value) for key, value in zip(claim_total_keys, claim_line[2:])}
                claims_list.append(total_claim_obj)

            # print()

            final_dicts.append(pat_info_dict)
    
    return final_dicts

class BcbsEngine:
    def __init__(self):
        pass

    def run(self,reader,file_path):
        
        try:
            print("running engine")
            headers, lines = get_all_page_lines(reader.pages, 21)
            jsons = extract_all_data(headers, lines)

            if jsons is not None:
                df = pd.json_normalize(jsons)
                pat_df = df[demo_keys][1:]
                claims_df = df['CLAIMS'][1:]
                claim_extract_rows = ["CHARGE AMOUNT", "PR AMOUNT", "CO AMOUNT", "OA AMOUNT", "PAID AMOUNT"]
                claim_rename_rows = {"CHARGE AMOUNT": "TOTAL CHARGE AMOUNT",
                                    "PR AMOUNT": "TOTAL PR AMOUNT",
                                    "CO AMOUNT": "TOTAL CO AMOUNT",
                                    "OA AMOUNT": "TOTAL OA AMOUNT",
                                    "PAID AMOUNT": "TOTAL PAID AMOUNT"}

                total_claims_data = []
                for item in claims_df:
                    if len(item) == 1:
                        total_rows = pd.json_normalize(item)[claim_extract_rows].iloc[0].rename(claim_rename_rows)
                    else:
                        total_rows = pd.json_normalize(item).iloc[-1][-5:]

                    total_claims_data.append(total_rows)

                total_claims_df = pd.DataFrame(total_claims_data)

                # Ensure total_rows has all required columns
                pat_df = pd.concat([pat_df.reset_index(drop=True), total_claims_df.reset_index(drop=True)], axis=1)
                file_name = file_path.split("/")[-1].replace(".pdf","")
                json_file_name = f"{file_name}.json"
                csv_file_name = f"{file_name}.csv"

                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    final_json=  json.dumps(jsons)
                    json_bytes = final_json.encode('utf-8')
                    zip_file.writestr(f"output.json", json_bytes)
                return zip_buffer

            else:
                print("called")
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    final_json=  json.dumps({[]})
                    json_bytes = final_json.encode('utf-8')
                    zip_file.writestr(f"output.json", json_bytes) 

                return zip_buffer
        except Exception as e:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    final_json=  json.dumps({"error":str(e)})
                    json_bytes = final_json.encode('utf-8')
                    zip_file.writestr(f"output.json", json_bytes) 
            return zip_buffer
            
        