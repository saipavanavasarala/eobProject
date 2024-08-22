import re,json
import pdfplumber

def extract_text_with_layout(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text(layout=True)  # Use layout=True to maintain spacing
    return text


def getAllData(pdf_path):
   extracted_text = extract_text_with_layout(pdf_path)
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
   return json.dumps(finalList,indent=3)


pdf_path=r"C:\\Users\\ankitha\\Downloads\\CHECK NUM 13218 VYTALISE.pdf"
res=getAllData(pdf_path)
print(res)