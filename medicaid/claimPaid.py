from .master import *


# Function to extract "CMS 1500 CLAIMS PAID" header type
def extract_claims_paid_tables(headers, lines):
    
    name_positions = [itr for itr, line in enumerate(lines) if 'NAME:' in line or 'TOTAL' in line]

    final_dicts = []
    claims_list = []
    pat_info_dict = {}

    # Extracting headers and adding to final dict only once
    payer_details = get_payer_details(headers)
    final_dicts.append(payer_details)
  
    for itr, line in enumerate(lines):
        if itr in name_positions and 'TOTAL' not in lines[itr]:

            recipient_id_loc = [rep_itr for rep_itr, val in enumerate(line) if 'RECIPIENT' in val]
            if len(line) > 7 and recipient_id_loc[0] != 3:
                start_itr = 2
                end_itr = recipient_id_loc[0]
                combined = line[start_itr:end_itr]
                line[2] = ' '.join(combined)
                for value in combined:
                    while value in line:  # This ensures all instances are removed
                        line.remove(value)
                
            table_start = itr
            table_end = get_next_value(name_positions,itr)
           
            
            demo_keys = ['FIRST NAME', 'LAST NAME', 'RECIPIENT ID', 'ICN', 'PAT ACCT NO', 
                         'SERVICE FROM', 'SERVICE THRU', 'BILLED AMOUNT', 'ALLOWED AMOUNT', 
                         'NON ALLOWED', 'COPAY', 'TPL', 'PAID AMOUNT']
            # Because the positions within the list are different, based on the claim header type, the list indicies below are different than the previous claim function
            pat_info_dict = {key: parse_value(value) for key, value in zip(demo_keys[:3], itemgetter(*[1, 2, 5])(lines[itr]))}
            pat_info_dict.update({key: parse_value(value) for key, value in zip(demo_keys[3:], lines[itr + 1])})
            claims_list = []
            pat_info_dict.update({'CLAIMS': claims_list})
            
            temp_lines = lines[table_start + 4:table_end]

            claim_keys = ['POS', 'PROC CD', 'MODIFIERS', 'UNITS', 'SRV FROM', 'SRV THRU', 
                                  'RENDERING PROVIDER', 'BILLED AMOUNT', 'ALLOWED AMOUNT', 'COPAY', 
                                  'PAID', 'DETAIL EOBS 1', 'DETAIL EOBS 2', 'NON-ALLOWED', 'TPL']
            
            # The length of the list may change based on the claim header type so this also is changed accordingly compared to the previous claim function
            for tempitr, claim_line in enumerate(temp_lines):

                mods_loc = [rep_itr for rep_itr, val in enumerate(claim_line) if len(val) == 2 and rep_itr != 0]
                if len(mods_loc) > 1:
                        modifiers = []
                        for loc in mods_loc:
                            modifiers.append(claim_line[loc])
                        for loc in mods_loc[1:]:
                            claim_line.pop(loc)
                        claim_line[2] = modifiers
                        claim_line.append(None)
                
                temp_claim_obj = {}
                if len(claim_line) >= 10 and '.' in claim_line[2]:
                    claim_line.insert(2, None)
                    
                if len(claim_line) >= 11:
                    pad_list_to_length_in_place(claim_line, 13)

                if len(claim_line) == 13 and claim_keys[0] not in claim_line:
                    # Indicies passed into the list change here as well based on the claim header type compared to the previous claim function
                    temp_claim_obj.update({key: parse_value(value) for key, value in zip(claim_keys, temp_lines[tempitr])})
                    temp_claim_obj.update({key: parse_value(value) for key, value in zip(claim_keys[13:], temp_lines[tempitr + 1])})
                    claims_list.append(temp_claim_obj)
            
            # check_claim_transformations(check_list, claims_list, 'POS')

        if 'TOTAL' in line:
            total_keys = ['TOTAL BILLED AMOUNT', 'TOTAL ALLOWED AMOUNT', 'TOTAL NON ALLOWED', 'TOTAL COPAY', 'TOTAL TPL', 'TOTAL PAID AMOUNT']
            # Indicies passed into the list change here as well based on the claim header type compared to the previous claim function
            final_dicts.append({key: parse_value(value) for key, value in zip(total_keys, lines[itr][5:])})
        
        if itr in name_positions and 'TOTAL' not in lines[itr]:
            final_dicts.append(pat_info_dict)
            pat_info_dict = {}

    return final_dicts

def get_total_by_patient_as_csv(json_list, csv_file_name):
        cols_needed = ['FIRST NAME', 'LAST NAME', 'RECIPIENT ID', 'PAT ACCT NO', 
                            'SERVICE FROM', 'SERVICE THRU', 'BILLED AMOUNT', 'ALLOWED AMOUNT', 
                            'NON ALLOWED', 'PAID AMOUNT']
        df = pd.DataFrame(json_list[1:])
        df[cols_needed].to_csv(csv_file_name, index=False)
        
def run_claim_paid(reader):
    claims_paid_pages = reader.pages
    claim_type = 'CMS 1500 CLAIMS PAID'
    #print(file_path.replace(' ','_').split('.'))
    fileName = r"CMS_1500_CLAIMS_PAID"#file_path.replace(' ','_').split('.')[0].split('/')[1]+claim_type.replace(' ', '_')
    temp_file_name = f'outputs/{fileName}'
    json_file_name = f'{temp_file_name}.json'
    csv_file_name = f'{temp_file_name}.csv'



    display(Markdown(f'## CLAIM TYPE: {claim_type}'))
    headers, lines = get_all_page_lines_by_claim_header_type(claims_paid_pages, claim_type)
    jsons = extract_claims_paid_tables(headers, lines)

    return jsons
# display(Markdown(f'```json\n{json.dumps(jsons, indent=4, default=custom_serializer)}\n```'))