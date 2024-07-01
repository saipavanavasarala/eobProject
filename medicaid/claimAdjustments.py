from .master import *
# Function to extract "CMS 1500 CLAIM ADJUSTMENTS" header type
def extract_claims_adjusted_tables(headers, lines):
    # The line below takes the page lines as a list of lists and gets the indicies where "NAME:" or "TOTAL" is mentioned in the list
    # This is used below to dynamically define the beginning and end of each table
    name_positions = [itr for itr, line in enumerate(lines) if 'NAME:' in line or 'TOTAL' in line]

    # Removing duplicate name positions when repeated across pages
    # only if the second row is not an adjustment column to handle minor differences in format
    # across files
    for itr, name_pos in enumerate(name_positions):
        if lines[name_positions[itr - 1]] == lines[name_pos] and '(' not in lines[name_pos + 1][4]:
            del name_positions[itr - 1]

    final_dicts = []
    claims_list = []
    pat_info_dict = {}
    # Extracting headers and adding to final dict only once
    payer_details = get_payer_details(headers)
    final_dicts.append(payer_details)
    # Looping through each line
    for itr, line in enumerate(lines):
        # Getting all indicies of the patient details based on the presence of "NAME:" and excluding "TOTAL" which is handled separately below
        if itr in name_positions and 'TOTAL' not in lines[itr]:
            # Combining middle and last name if it exists
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
          
            # Defining demographic keys
            demo_keys = ['FIRST NAME', 'LAST NAME', 'RECIPIENT ID', 
                         'ADJUSTED ICN', 'ADJUSTED PAT ACCT NO', 'ADJUSTED SERVICE FROM', 'ADJUSTED SERVICE THRU', 
                         'ADJUSTED BILLED AMOUNT', 'ADJUSTED ALLOWED AMOUNT', 'ADJUSTED NON ALLOWED', 'ADJUSTED COPAY', 
                         'ADJUSTED TPL', 'ADJUSTED PAID AMOUNT', 
                         'ICN', 'PAT ACCT NO', 'SERVICE FROM', 'SERVICE THRU', 'BILLED AMOUNT', 'ALLOWED AMOUNT', 'NON ALLOWED', 
                         'COPAY', 'TPL', 'PAID AMOUNT']
            
            if 'NAME:' in line:
                # Isolating the values within each line so that they can be assigned appropriately to the headers above
                # Updating the patient_info_dict once the keys and values are zipped
                pat_info_dict = {key: parse_value(value) for key, value in zip(demo_keys[:3], itemgetter(*[1, 2, 5])(lines[itr]))}
                
                # Getting the demogrpahic info in the lines below the line with "NAME:" in it
                pat_info_dict.update({key: parse_value(value) for key, value in zip(demo_keys[3:], lines[itr + 1])})
                pat_info_dict.update({key: parse_value(value) for key, value in zip(demo_keys[13:], lines[itr + 2])})

                # Claim adjustment tables sometimes have net overpayment at the end of the table so included this specific to this function
                # Adding it to the patient dict at the 
                if 'NET' in lines[table_end - 1]:
                    pat_info_dict.update({'NET OVERPAYMENT (AR)': parse_value(lines[table_end - 1][-1])})

                # Initializing the claims list for later
                claims_list = []
                pat_info_dict.update({'CLAIMS': claims_list})

                # Isolating the first and last index of each table by adding/subtracting from the index where "NAME:" is in the list
                # Setting all rows of the table to a temporary list to loop through below
                temp_lines = lines[table_start + 4:table_end]
            
            # Defining claim keys
            claim_keys = ['POS', 'PROC CD', 'MODIFIERS', 'UNITS', 'SRV FROM', 'SRV THRU', 'RENDERING PROVIDER', 'BILLED AMOUNT', 
                                  'ALLOWED AMOUNT', 'COPAY', 'PAID', 'DETAIL EOBS 1', 'DETAIL EOBS 2', 'ALLOWED', 'NON-ALLOWED']
            
            # Looping through each row of the table lines
            for tempitr, claim_line in enumerate(temp_lines):
                # Looking for more than one modifier
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
                # Padding table with None if MODIFIERS is not in the table row and if only one DETAIL EOBS is present in that table row
                if len(claim_line) == 11 and '.' in claim_line[2]:
                    claim_line.insert(2, None)
                if len(claim_line) == 12:
                    pad_list_to_length_in_place(claim_line, 13)

                # Once padding is complete, checking for length to exclude column headers in between pages
                # Because claims are multi-line, using the enumeration to get the second row for each claim row
                if len(claim_line) == 13 and claim_keys[0] not in claim_line:
                    
                    temp_claim_obj.update({key: parse_value(value) for key, value in zip(claim_keys, temp_lines[tempitr])})
                    temp_claim_obj.update({key: parse_value(value) for key, value in zip(claim_keys[13:], temp_lines[tempitr + 1])})
                    claims_list.append(temp_claim_obj)
                    
        # Handling Total values at the end of each claim header type
        if 'TOTAL' in line and 'CMS' in line:
            temp_total_obj = {}
            # Defining total keys
            total_keys = ['TOTAL BILLED AMOUNT', 'TOTAL ALLOWED AMOUNT', 'TOTAL NON ALLOWED', 'TOTAL COPAY', 
                          'TOTAL TPL', 'TOTAL PAID AMOUNT', 'TOTAL NO OF ADJUSTMENTS']
            temp_total_obj.update({key: parse_value(value) for key, value in zip(total_keys, lines[itr][5:])})
            
            # Handling total adustment count with totals
            if lines[itr - 1][-2] == 'ADJ:':
                temp_total_obj.update({total_keys[6]: parse_value(lines[itr - 1][-1])})

            # Adding to overall list only once
            final_dicts.append(temp_total_obj)

        # Adding entire patient json with claims to final_dicts list and reinitialzing pat_info_dict for the next loop
        if itr in name_positions and 'TOTAL' not in lines[itr]:
            final_dicts.append(pat_info_dict)
            pat_info_dict = {}

    return final_dicts

# Setting up sample of pages
def run_claim_adjustments(reader):
    claims_adjusted_pages = reader.pages

    # Displaying claim header type
    claim_type = 'CMS 1500 CLAIM ADJUSTMENTS'
    display(Markdown(f'## CLAIM TYPE: {claim_type}'))

    # Converting pages to headers and lines
    headers, lines = get_all_page_lines_by_claim_header_type(claims_adjusted_pages, claim_type)

    # Running the above function
    jsons= extract_claims_adjusted_tables(headers, lines)

    return jsons
