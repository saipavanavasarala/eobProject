import re 
import pdfplumber
import json

def extract_text_with_layout(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text(layout=True)  # Use layout=True to maintain spacing
    return text
 
def split_tab_Data(pdf_path):
   extracted_text = extract_text_with_layout(pdf_path)
   start_pattern='Patient Name:'
   end_pattern='Note:AllInquiriesshouldreferencetheIDnumberaboveforpromptresponse.'
   pattern = re.compile(fr'{re.escape(start_pattern)}(.*?)({re.escape(end_pattern)})', re.DOTALL) 
   split_data=re.findall(pattern,extracted_text)
   return split_data


def getAllData(reader_path,pdf_path):
    HeaderKeys=['SERVICE DATES','PL','SERVICE CODE','NUM. SVCS','SUBMITTED CHARGES','NEGOTIATED AMOUNT','COPAY AMOUNT','NOT PAYABLE','SEE REMARKS','DEDUCTIBLE','CO INSURANCE','PATIENT RESP','PAYABLE AMOUNT']
    TotalAmtKeys=['SUBMITTED CHARGES','NOT PAYABLE','CO INSURANCE','PATIENT RESP','PAYABLE AMOUNT']

    split_data=split_tab_Data(pdf_path)
    finalList=[]
    for key,data in enumerate(split_data):
        patientName=data[0].split('\n')[0].strip()
        ClaimId=re.findall('(?<=ClaimID:)(.*)(Recd:)',data[0])[0][0]
        Recd=re.findall('(?<=Recd:)(.*)(MemberID:)',data[0])[0][0]
        MemberId=re.findall('(?<=MemberID:)(.*)(PatientAccount:)',data[0])[0][0]
        PatientAccount=re.findall('(?<=PatientAccount:)(.*)',data[0])[0]
        Member=re.findall('(?<=Member:)(.*)(DIAG:)',data[0])[0][0].rstrip()
        Diag=re.findall('(?<=DIAG:)(.*)',data[0])[0]
        GroupName=re.findall('(?<=GroupName:)(.*)(GroupNumber:)',data[0])[0][0].strip()
        GroupNo=re.findall('(?<=GroupNumber:)(.*)',data[0])[0]
    
        #get table data
        pattern=re.compile(r'(\d{2}/\d{2}/\d{2})\s+(\d+)\s+(\S+)\s+(\d{1}.\d{1}|\s)\s+(.*)')
        tabData=pattern.findall(data[0])
    
            
            
        #print(tabData)
        TabData=[]
        for item in tabData:
            itemDetails=[]
            itemDetails.extend([item[0],item[1],item[2],item[3]])
            itemDetails.extend(item[4].split())
        
            if len(itemDetails)==8:
                itemDetails.insert(5,'')
                itemDetails.insert(6,'')
                itemDetails.insert(9,'')
                itemDetails.insert(10,'')
                itemDetails.insert(11,'')
            elif len(itemDetails)==9:
                itemDetails.insert(5,'')
                itemDetails.insert(6,'')
                itemDetails.insert(9,'')
                itemDetails.insert(10,'')       
            elif len(itemDetails)==10:
                itemDetails.insert(5,'')
                itemDetails.insert(6,'')
                itemDetails.insert(9,'')
        
            TabData.append(dict(zip(HeaderKeys,itemDetails)))
    
    #preprocessing the where submitted is present IN LINE
        lines=data[0].split('\n')
    
        submittedLine=[]
        for line in lines:
            if 'SUBM ITTED' in line:
            #print(patientName)
                split_line=line.split()
                if len(split_line)==6:
                    split_line[3]=split_line[3]+split_line[4]
                    split_line.remove(split_line[4])
                    split_line.insert(1,'')
                    split_line.insert(5,'SUBMITTED')
                    split_line.insert(6,'SUBMITTED')
                    split_line.insert(7,'SUBMITTED')
                    split_line.insert(9,'SUBMITTED')
                    split_line.insert(10,'SUBMITTED')
                    split_line.insert(11,'SUBMITTED')
                    split_line.insert(12,'SUBMITTED')
                
                elif len(split_line)==5:
                    split_line[2]=split_line[2]+split_line[3]
                    split_line.remove(split_line[3])
                    split_line.insert(0,'')
                    split_line.insert(1,'')
                    split_line.insert(5,'SUBMITTED')
                    split_line.insert(6,'SUBMITTED')
                    split_line.insert(7,'SUBMITTED')
                    split_line.insert(9,'SUBMITTED')
                    split_line.insert(10,'SUBMITTED')
                    split_line.insert(11,'SUBMITTED')
                    split_line.insert(12,'SUBMITTED')
                submittedLine.append(split_line)
    
        if submittedLine:
            for eachLine in submittedLine:
                SubmittedDict=dict(zip(HeaderKeys,eachLine))
                #print(SubmittedDict)
                TabData.insert(int(f'{key}'),SubmittedDict)
                #print(key)
    
        IssuedAmt=re.findall('(?<=ISSUEDAMT:)(.*)',data[0])[0].strip()
    #calculating Total Amount
        Total=re.findall('(?<=TOTALS)(.*)',data[0])[0].split()   
        if len(Total)==3:
            Total.insert(2,'')
            Total.insert(3,'')
        elif len(Total)==4:
            Total.insert(2,'')
        totalAmt=dict(zip(TotalAmtKeys,Total))
    
        TotalPatientRes=re.findall('(?<=TotalPatientResponsibility:)(.*)',data[0])[0].strip()
        claimPayment=re.findall('(?<=ClaimPayment:)(.*)',data[0])[0].strip()

    #print(TabData)
        finalList.append({
            'Patient Name': patientName,
            'Claim Id': ClaimId,
            'RECD': Recd,
            'Member Id': MemberId,
            'Patient Account': PatientAccount,
            'Member': Member,
            'DIAG': Diag,
            'Group Name': GroupName,
            'Group No': GroupNo,
            'Table Details': TabData,
            'Issued Amt':IssuedAmt,
            'Total Amount Details':totalAmt,
            'Total patient Responsibility':TotalPatientRes,
            'Claim Payment':claimPayment
                })   
    return finalList







  
# pdf_path = "C:\\Users\\ankitha\\Downloads\\882413601000531_05.16.2024_$3080.21(Aetna 143 Pages).pdf"
# res=getAllData("",pdf_path)
# print(res)
