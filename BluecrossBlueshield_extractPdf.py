import re,json
import pdfplumber

def extract_text_with_layout(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text(layout=True)  # Use layout=True to maintain spacing
    return text


def get_payee_Details(extracted_text):
    payeeTaxId=re.findall("(?<=Payee Tax ID:)(.*)(Payee Name:)",extracted_text)[0][0].strip()
    payeeName=re.findall("(?<=Payee Name:)(.*)(\n)(.*)",extracted_text)[0]
    payeeName=payeeName[0].strip()+" "+payeeName[2].strip()
    payeeId=re.findall("(?<=Payee ID:)(.*)(Payee Address:)",extracted_text)[0][0].strip()

    CheckEtfTraceNo=re.findall("(?<=Check/EFT Trace Number:)(.*)(\n)(.*)",extracted_text)[0]
    EtfTraceNo=CheckEtfTraceNo[0].strip()
    PayeeAdress=re.findall("(?<=Payee Address:)(.*)(\n)(.*)",extracted_text)[0][2].strip()
    payeeAdress=PayeeAdress+" "+CheckEtfTraceNo[2].strip()
    paymentAmt=re.findall("(?<=Payment Amount:)(.*)",extracted_text)[0].strip()
    CheckEtfDate=re.findall("(?<=Check/EFT Date:)(.*)",extracted_text)[0].strip()
    productionEndDate=re.findall("(?<= Production End Cycle Date:)(.*)",extracted_text)[0].strip()
    payeeDetails={'Payee Tax ID':payeeTaxId,'Payee Name':payeeName,'Payee ID':payeeId,'Check ETF Trace No':EtfTraceNo,
                'Payee Adress':payeeAdress,'Payment Amount':paymentAmt,'Check ETF Date':CheckEtfDate,'productionEndDate':productionEndDate}
    return payeeDetails


def get_ProviderAdjustment_details(extracted_text):
    providerAdjustmentKeys=['Provider Adjustment code','Provider Adjustment Identifier','Provider Adjustment Amount']
    start_pattern='Provider Adjustments'
    end_pattern=' Patient Name:'
    pattern = re.compile(fr'{re.escape(start_pattern)}(.*?)({re.escape(end_pattern)})', re.DOTALL) 
    PAtext=re.findall(pattern,extracted_text)[0][0]
    PAtextList=PAtext.split('\n')
    providerAdjustmentRecords=[]
    for line in PAtextList[2:]:
        records=line.split()
        if records:
            PatextRes=dict(zip(providerAdjustmentKeys,records))
            providerAdjustmentRecords.append(PatextRes)
    return providerAdjustmentRecords

def get_tableRecords(extracted_text):
    LineDetailsHeaderKey=['Line ctrl Number','Date of Service','Rend Prov Id','Rev','Sub Proc/Modifier unit','Adjud Proc/Modifier units','Remark/Payer code','Supp Info(AMT)','Charge','Adjustments(Qty)1','Adj Amount1','Payment','Adjustments(Qty)2','Adj Amount2']
    PatientDetailsHeaderKey=['Patient Name','Claim Number','Claim Date','Claim Status Code','Patient ID','Group/policy',
                            'Facility Type','Claim Charge','Patient control Number','Contact HDR','Claim Frequency','Claim Payment'
                            'Rendering Prov','RenderingProvID','Claim Recived Date','Patient Resp','Orginal Ref Num']


    AllRecordDetails=[]
    #Getting patient Details and line Details
    AllDetails=extracted_text.split("Patient Name:")[1:]
    for key,data in enumerate(AllDetails):
        combinedDetails={}
        HeaderDetails=[]
        patientDetails=data.split("Line Details")[0]
        patientName=patientDetails.split("Claim Number:")[0]
        claimNo=re.findall("(?<=Claim Number:)(.*)(Claim Date:)",patientDetails)[0][0].strip()
        claimDate=re.findall("(?<=Claim Date:)(.*)(Claim Status Code:)",patientDetails)[0][0].strip()
        claimStatusCode=re.findall("(?<=Claim Status Code:)(.*)",patientDetails)[0].strip()
        patientId=re.findall("(?<=Patient ID:)(.*)(Group / Policy:)",patientDetails)[0][0].strip()
        Group_policy=re.findall("(?<=Group / Policy:)(.*)(Facility Type:)",patientDetails)[0][0].strip()
        Facility_type=re.findall("(?<=Facility Type:)(.*)(Claim Charge:)",patientDetails)[0][0].strip()
        claimCharge=re.findall("(?<=Claim Charge:)(.*)",patientDetails)[0].strip()
        patientCtrlNo=re.findall("(?<=Patient Ctrl Nmbr:)(.*)(Contract Hdr:)",patientDetails)[0][0].strip()
        ContactHdr=re.findall("(?<=Contract Hdr:)(.*)(Claim Frequency:)",patientDetails)[0][0].strip()
        claimFrequency=re.findall("(?<=Claim Frequency:)(.*)(Claim Payment:)",patientDetails)[0][0].strip()
        claimPayment=re.findall("(?<=Claim Payment:)(.*)",patientDetails)[0].strip()
        RenderingProv=re.findall("(?<=Rendering Prvd:)(.*)(Rendering Prv ID:)",patientDetails)[0][0].strip()
        RenderingProvID=re.findall("(?<=Rendering Prv ID:)(.*)(Claim Received Date:)",patientDetails)[0][0].strip()
        if RenderingProvID=="":
            RenderingProvID="None"
        claimRecivedDate=re.findall("(?<=Claim Received Date:)(.*)(Patient Resp:)",patientDetails)[0][0].strip()
        patientResp=re.findall("(?<=Patient Resp:)(.*)",patientDetails)[0].strip()
        OrginalRefNum=re.findall("(?<=Original Ref Nmbr:)(.*)",patientDetails)[0].strip()
        if OrginalRefNum=="":
            OrginalRefNum="None"
    
        HeaderDetails.extend([patientName,claimNo,claimDate,claimStatusCode,patientId,Group_policy,Facility_type,claimCharge,
                            patientCtrlNo,ContactHdr,claimFrequency,claimPayment,RenderingProv,RenderingProvID,claimRecivedDate,
                            patientResp,OrginalRefNum
                            ])
        Header_Details=dict(zip(PatientDetailsHeaderKey,HeaderDetails))
        #line Details
        line_pattern=re.compile(r"(\d \d+)\s+(\d{2}/\d{2}/\d{4}\s-)\s+([A-Z]{2}:\w+\s+/\s+/\s+\S+|[A-Z]{2}:\w+\s+/\s+\d+\s+/\s+\S+)(\s+\w+|\s+)(.*)\n(.*)")
        
        record_line=re.findall(line_pattern,data)  
        RecordsDetails=[]
        for record in record_line:
            record=list(record)
            split_element1=record[4].split()            #first line 
            if len(split_element1)==6:
                split_element1[0]=split_element1[0]+""+split_element1[1]
                split_element1.remove(split_element1[1])
            elif len(split_element1)==4:
                split_element1.insert(0,"")
            
            split_element2=record[5].split()   #second line
            if len(split_element2)==1:
                serviceDate="".join([record[1],split_element2[0]])
                record.insert(1,serviceDate)
                split_element2.insert(0,"")
                split_element2.insert(1,"")
                split_element2.remove(split_element2[2])
            elif len(split_element2)==3:
                serviceDate="".join([record[1],split_element2[0]])
                record.insert(1,serviceDate)
                split_element2.remove(split_element2[0])
            record.remove(record[2])
        
            
            updatedRecordList=[record[0],record[1],"","","",record[2],record[3].strip(),*split_element1,*split_element2]
            record_dict=dict(zip(LineDetailsHeaderKey,updatedRecordList))
            RecordsDetails.append(record_dict)

        combinedDetails['HeaderDetails']=Header_Details
        combinedDetails['RecordDetails']=RecordsDetails
        AllRecordDetails.append(combinedDetails)
    return AllRecordDetails


def getAllData(pdf_path):
    extracted_text=extract_text_with_layout(pdf_path)
    payeeDetails=get_payee_Details(extracted_text)
    providerAdjustmentDetails=get_ProviderAdjustment_details(extracted_text)
    AllRecordDetails=get_tableRecords(extracted_text)
    #combine all the details
    AllRecordDetails.insert(0,{'payee Details':payeeDetails})
    AllRecordDetails.insert(1,{'Provider Adjustment Records':providerAdjustmentDetails}) 
    return json.dumps(AllRecordDetails,indent=3)


pdf_path=r"D:\\gitOcr\pdfs\\24137B100108860700 (120 Pges $5,867.31).pdf"
res=getAllData(pdf_path)
print(res)

    