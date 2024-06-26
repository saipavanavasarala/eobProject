from .master import *
from operator import itemgetter
import json
from IPython.display import display, Markdown, Image
from PyPDF2 import PdfReader
import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import os
import pandas as pd
from io import BytesIO
import zipfile



def wEngine(reader):
    headers, pages = get_all_page_lines_by_claim_header_type(reader.pages)

    claim_keys = ['FROM', 'THRU', 'PROC', 'MD', 'REV', 'UNT', 'CHARGE AMT',
                'ALLOWED', 'PAYMENT', 'ADJ AMOUNT', 'GRP' , 'RSN', 'REM1', 'REM2' 
                ,'ADJ AMOUNT 2', 'GRP 2' , 'RSN 2']

    final_dict = []
    for itr, lines in enumerate(pages):

        name_positions = [itr for itr, line in enumerate(lines) if 'PROC' in line or 'TOTALS' in line]
        if name_positions:

            table = lines[name_positions[0] + 1:name_positions[1] + 1]

            patient_dict = {}
            claims_list = []
            for patient_itr, patient_line in enumerate(headers[itr]):
                if 'NAME' in patient_line[0]:
                    patient_dict["LAST NAME"] = patient_line[0].split(':')[1].strip(',')
                    patient_dict["FIRST_NAME"] = patient_line[1]
                    patient_dict["TOTAL CHARGE"] = patient_line[-1]
                if 'ACCOUNT' in patient_line[0]:
                    patient_dict["ACCOUNT NO"] = patient_line[2]
                    patient_dict["TOTAL PAYMENT"] = patient_line[-1]
                if 'CCN' in patient_line[0]:
                    patient_dict["CCN"] = patient_line[1].split(':')[1]
                    patient_dict["TOTAL CONTRACTUAL"] = patient_line[-1]
                if 'DEDUCTIBLE' in patient_line:
                    patient_dict["TOTAL DEDUCTIBLE AMT"] = patient_line[-1]
                if 'COINSURANCE' in patient_line:
                    patient_dict["TOTAL COINSURANCE AMT"] = patient_line[-1]
                if 'CO-PAYMENT' in patient_line:
                    patient_dict["TOTAL CO-PAYMENT AMT"] = patient_line[-1]
                if 'REMARK:' in patient_line[0]:
                    patient_dict["ADJ AMT"] = patient_line[-1]
                if 'TOB:' in patient_line[0]:
                    patient_dict["TOB"] = patient_line[0].split(':')[1]
            patient_dict = dict(sorted(patient_dict.items()))
            patient_dict.update({'CLAIMS': claims_list})
            
            
            for claim_itr, claim_line in enumerate(table):
                temp_claim_obj = {}
                if 'CLAIM' not in claim_line[0]:
                    if len(claim_line) >= 3:
                        if '-' not in claim_line[1]:
                            claim_line.insert(1, None)
                        if '.' in claim_line[3]:
                            claim_line.insert(3, None)
                        if '.' in claim_line[4]:
                            claim_line.insert(4, None)
                        if len(claim_line[10]) != 2:
                            claim_line.insert(11, claim_line[10][:2])
                            claim_line.insert(12, claim_line[10][2:])
                            claim_line.remove(claim_line[10])
                        if len(claim_line[11]) > 3:
                            claim_line.insert(12, split_value(claim_line[11])[0])
                            claim_line.insert(13, split_value(claim_line[11])[1])
                            claim_line.remove(claim_line[11])


                        if len(claim_line)==12:         
                            claim_line.insert(12,None)
                            claim_line.insert(13,None)
                        if len(claim_line)==13:
                            claim_line.insert(13,None)
                        if len(table[claim_itr + 1]) < 3:
                            temp_val = table[claim_itr + 1]
                            claim_line.append(temp_val[0])
                            claim_line.append(temp_val[1][:2])
                            claim_line.append(temp_val[1][2:])

                        # issue with first column appended to date in 2nd column
                        claim_line[0] = claim_line[0][1:]

                        pad_list_to_length_in_place(claim_line, len(claim_keys))
                        temp_claim_obj.update({key: parse_value(value) for key, value in zip(claim_keys, claim_line)})
                        claims_list.append(temp_claim_obj)

            final_dict.append(patient_dict)

    final_json=  json.dumps(final_dict)
    json_bytes = final_json.encode('utf-8')

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
        zip_file.writestr(f"output.json", json_bytes)

    return zip_buffer
    
    


    