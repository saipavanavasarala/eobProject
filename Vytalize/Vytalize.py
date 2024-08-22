import re,json
import pdfplumber
from io import BytesIO
import zipfile

class VytalizeEngine:

    def extract_text_with_layout(self,pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text(layout=True)  # Use layout=True to maintain spacing
        return text
    

    def getAllData(self,pdf_path):
        extracted_text = self.extract_text_with_layout(pdf_path)
        splitted_text=extracted_text.split("Claim:")
        HeaderKeys=['DOS','CPT code','Modifier','Billed Amount','Units','Contracted','Copay','Coinsurance','Deductible','CMS PMT','Adjustment','Seq Amt','MIPS Amt','Paid']
        finalList=[]
        for i in  range(1,len(splitted_text)):
            lines=splitted_text[i].split('\n')
            claim=lines[0].split()[0]
            Member=re.findall('(?<=Member:)(.*)(Member ID:)',splitted_text[i])[0][0].strip()
            MemberId=re.findall('(?<=Member ID:)(.*)(Patient Number:)',splitted_text[i])[0][0].strip()
            PatientNumber=re.findall('(?<=Patient Number:)(.*)',splitted_text[i])[0].strip()
            
            #getting table data
            pattern=re.compile(r'(\d{1}/\d{2}/\d{2})\s+(\S+)\s+(.*)|(\d{1}/\d{1}/\d{2})\s+(\S+)\s+(.*)')
            tabData=pattern.findall(splitted_text[i])
            TabDetails=[]
            for details in tabData:
                filtered_tuple = tuple(item for item in details if item)
                splited_elements=filtered_tuple[2].split()
                UpdatedList=[filtered_tuple[0], filtered_tuple[1], *splited_elements]
                if len(UpdatedList)==13:
                    UpdatedList.insert(2,'')   
                TabDetailsDict=dict(zip(HeaderKeys,UpdatedList))
                #print(TabDetailsDict)
                TabDetails.append(TabDetailsDict)
            #Total
            total=re.findall('(?<=Total for patient #)(.*)',splitted_text[i])[0].split()[1:]
            totalDict=dict(zip(HeaderKeys[3:],total))
            
            finalList.append(
            {
                'Claim':claim,
                'Memeber':Member,
                'Memeber ID':MemberId,
                'Patient Number':PatientNumber,
                'Claim Details':TabDetails,
                'Total':totalDict
            })  
        return finalList

    def run(self,reader,pdfPath):

        data = self.getAllData(pdfPath)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            final_json=  json.dumps(data)
            json_bytes = final_json.encode('utf-8')
            zip_file.writestr(f"output.json", json_bytes)

        return zip_buffer



