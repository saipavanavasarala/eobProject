import re
from io import BytesIO
import zipfile
import json 

def extract_text_all_pages(reader):
    pages=reader.pages
    all_text=""
    for i in range(2,len(pages)):
        page_text=pages[i].extract_text()
        all_text+=page_text



    table_start='EXPL CD:FOR INQUIRIES CALL:'
    table_end='TOTAL NET PAID'
    pattern = re.compile(fr'{re.escape(table_start)}(.*?)({re.escape(table_end)})', re.DOTALL) 
    # Find all occurrences
    table_data = pattern.findall(all_text)
    tableHeaders=['SERVICE DATE(S)','SERVICE/REVENUECODE(S)','COUNT DAYS','POS','CHARGE','ALLOWED','DEDUCTIBLE','COINSURANCE COPAYMENTAMOUNT','CONTRACTUALDIFFERENCE','TPP','PROV RESP AMOUNT','EXPL/ANSICODE(S)',"INSURED'S RESP AMOUNT","NET PAID"]
    TotalHeaders=['CHARGE','ALLOWED','DEDUCTIBLE','COINSURANCE COPAYMENTAMOUNT','CONTRACTUALDIFFERENCE','TPP','PROV RESP AMOUNT',"INSURED'S RESP AMOUNT","NET PAID"]   #total amount Headers

    final_res=[]

    for i in range(len(table_data)):
        res_tab={}
        entries=[]
        if "CONCORD LIFE SCIENCES" not in table_data[i][0]:
            lines = [line.strip() for line in table_data[i][0].splitlines() if line.strip()]
            for j in range(len(lines)):
                if len(lines[j].split())>=16:
                    data=lines[j].split()
                    data[0]=data[0]+' '+data[1]
                    data[12]=data[12]+' '+data[13]  
                    data.pop(1)
                    data.pop(12)
                    if len(data) == len(tableHeaders):
                        entry = dict(zip(tableHeaders, data))
                        entries.append(entry)
                        
                elif 'TOTAL:' in lines[j].split():
                    data=lines[j].split()[1:]
                    if len(TotalHeaders)==len(data):
                        entry=dict(zip(TotalHeaders,data))
                        res_tab['Total']=entry
                        
                elif 'INTEREST' in lines[j].split():
                    data=lines[j].split()[1]
                    res_tab['INTEREST']=data
            res_tab['Table Details']=entries
            
            
        elif "CONCORD LIFE SCIENCES" in table_data[i][0]:
                start="CONCORD LIFE SCIENCES "
                end="EXPL CD:FOR INQUIRIES CALL:"
                pattern = re.compile(fr'{re.escape(start)}(.*?){re.escape(end)}', re.DOTALL)
                cleaned_text = (pattern.sub(start + " " + end, table_data[i][0])).replace("CONCORD LIFE SCIENCES  EXPL CD:FOR INQUIRIES CALL:","")
                lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
                for j in range(len(lines)):
                    if len(lines[j].split())>=16:
                        data=lines[j].split()
                        data[0]=data[0]+' '+data[1]
                        data[12]=data[12]+' '+data[13]
                        data.pop(1)
                        data.pop(12)
                        if len(data) == len(tableHeaders):
                            entry = dict(zip(tableHeaders, data))
                            entries.append(entry)
                        
                    elif 'TOTAL:' in lines[j].split():
                        data=lines[j].split()[1:]
                        if len(TotalHeaders)==len(data):
                            entry=dict(zip(TotalHeaders,data))
                            res_tab['Total']=entry
                        
                    elif 'INTEREST' in lines[j].split():
                        data=lines[j].split()[1]
                        res_tab['INTEREST']=data
                res_tab['Table Details']=entries
            
        final_res.append(res_tab)
    
    cleaned_text=all_text.replace("\n","")

    start_pattern="PATIENT NAME INSURED'S"
    end_pattern='APPEALS CODE:'

    pattern = re.compile(fr'{re.escape(start_pattern)}(.*?)({re.escape(end_pattern)})', re.DOTALL) 
    first_row_data=pattern.findall(cleaned_text)

    start='TOTAL NET PAID'
    end='APPEALS CODE:'
    pattern = re.compile(fr'{re.escape(start)}(.*?)({re.escape(end)})', re.DOTALL) 

    # Find all occurrences
    table_data = pattern.findall(cleaned_text)
    table_data.insert(0,first_row_data[0])

    keys=['PATIENT NAME','MEMBER ID','STATE/ALT ID','PATIENT ACCOUNT','CLAIM NUMBER','RECEIVED DATE','FOR ENQUIRES CALL']

    for i in range(len(table_data)):
        pattern=re.compile(r"""([A-Z]+,[A-Z]+\s\S |[A-Z]+,[A-Z]+)
                                \s+
                                (\d{9}|\S+)
                                \s+
                                (\d{9}|\S+)
                                \s+
                                (\S+)
                                \s+
                                (\d+)
                                \s+
                                (\d{2}/\d{2}/\d{4})
                                \s+
                                (\S+\s\d+-\d+)       
        """, re.VERBOSE)

        matches = pattern.findall(table_data[i][0])
        if matches!=[]:
            entry=dict(zip(keys, matches[0]))
            final_res[i]['HeaderDetails']=entry

    print(final_res)
    reordered_data = [
    {   'Headers Details':item['HeaderDetails'],
        'Table Details': item['Table Details'],
        'TotalAmount': item['Total'],
        'INTEREST': item['INTEREST']
    }
    for item in final_res
    ]


    
            
    return reordered_data
    

class WellPointEOBEngine:
    def __init__(self):
        pass 

    def run(self,reader,pdfPath):
        data = extract_text_all_pages(reader)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            final_json=  json.dumps(data)
            json_bytes = final_json.encode('utf-8')
            zip_file.writestr(f"output.json", json_bytes)

        return zip_buffer
