from .master import *
# Function to extract "CMS 1500 CLAIMS DENIED" header type
def extract_claims_denied_tables(headers, lines):
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
            
            # Adding additional business logic due to some demographic data rows having an extra row with 
            # redundant PAT ACCT NO. value while others did not
            if 'SERVICE' not in lines[table_start + 2]:
                table_start = table_start + 5
            else:
                table_start = table_start + 4
            table_end = table_end - 1

            demo_keys = ['FIRST NAME', 'LAST NAME', 'RECIPIENT ID','ICN', 'PAT ACCT NO', 
                         'SERVICE FROM', 'DATES THRU', 'BILLED AMOUNT', 'COPAY','TPL AMOUNT']
            pat_info_dict = {key: parse_value(value) for key, value in zip(demo_keys[:3], itemgetter(*[1,2,5])(lines[itr]))}
            pat_info_dict.update({key: parse_value(value) for key, value in zip(demo_keys[3:], lines[itr + 1])})
            
            claims_list = []
            pat_info_dict.update({'CLAIMS': claims_list})

            temp_lines = lines[table_start: table_end + 1]

            claim_keys = ['POS', 'PROC CD', 'MODIFIERS', 'UNITS', 'SERVICE FROM', 'DATES THRU', 
                                'RENDERING PROVIDER', 'BILLED AMOUNT', 'COPAY', 
                                'DETAIL EOBS 1' , 'DETAIL EOBS 2', 'DETAIL EOBS 3']
            
            # Extra if statement added to handle certain rows with a 3rd DEATIL EOBS value
            # Future To Do: Create list and add DETAIL EOBS to list instead of separate key-value pairs
            for claim_line in temp_lines:
                mods_loc = [rep_itr for rep_itr, val in enumerate(claim_line) if len(val) == 2 and rep_itr != 0]
                if len(mods_loc) > 1:
                        modifiers = []
                        for loc in mods_loc:
                            modifiers.append(claim_line[loc])
                        for loc in mods_loc[1:]:
                            claim_line.pop(loc)
                        claim_line[2] = modifiers
                        claim_line.append(None)
                        
                if len(claim_line) >= 9 and '.' in claim_line[2]:
                    claim_line.insert(2, None)
                if len(claim_line) == 10:
                    pad_list_to_length_in_place(claim_line, 12)
                if len(claim_line) == 12 and claim_keys[0] not in claim_line:
                    claim_dict = {key: parse_value(value) for key, value in zip(claim_keys, claim_line)}
                    claims_list.append(claim_dict)
                    
        if 'TOTAL' in line:
            total_keys = ['TOTAL BILLED', 'TOTAL COPAY','TOTAL TPL AMOUNT']
            final_dicts.append({key: parse_value(value) for key, value in zip(total_keys, lines[itr][-3:])})
        
        if itr in name_positions and 'TOTAL' not in lines[itr]:
            final_dicts.append(pat_info_dict)
            pat_info_dict = {}

    return final_dicts

def run_claim_denied(reader):
    claims_paid_pages = reader.pages
    claim_type = 'CMS 1500 CLAIMS DENIED'
    display(Markdown(f'## CLAIM TYPE: {claim_type}'))
    headers, lines = get_all_page_lines_by_claim_header_type(claims_paid_pages, claim_type)
    jsons = extract_claims_denied_tables(headers, lines)

    return jsons

# display(Markdown(f'```json\n{json.dumps(jsons, indent=4, default=custom_serializer)}\n```'))