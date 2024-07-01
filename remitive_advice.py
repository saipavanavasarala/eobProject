import re
from PyPDF2 import PdfReader
from datetime import datetime

def getText(pages):
    all_text=""
    for i in range(len(pages)):
        text=pages[i].extract_text()
        all_text+=text
    return all_text
 
def DateTimeFormating(date_str):
    # Parse the string into the desired format
    date_obj = datetime.strptime(date_str, '%m%d%y')
    # Format the date object into 'month date year' format
    formatted_date = date_obj.strftime('%Y-%m-%d')
    return formatted_date
 
def get_HeaderDetails(headerData):
   name=re.findall('(?<=NAME )(.*)(MID)',headerData)
   mid=re.findall('(?<=MID )(.*)(ACNT)',headerData)
   acnt=re.findall('(?<=ACNT )(.*)(ICN)',headerData)
   asg=re.findall('(?<=ASG )(.*)(MOA)',headerData)
   moa=re.findall('(?<=MOA )(.*)',headerData)
   if name and mid and acnt and asg and moa:
      name=name[0][0].rstrip()
      mid=mid[0][0].rstrip()
      acnt=acnt[0][0].rstrip()
      asg=asg[0][0]
      moa=moa[0]
   HeaderDetails={
         'Name':name,
         'MID':mid,
         'ACNT':acnt,
         'ASG':asg,
         'MOA':moa
      }
   return HeaderDetails


def GetTabDetails(lines):
   RecordDetails=[] 
   for line in lines:
      recordData=line.split()
         #print(recordData)
      if len(recordData)==12:
         entry={
                  'PERF PROV':recordData[0],
                  'SERV DATE':DateTimeFormating(recordData[1]),
                  'POS':recordData[2],
                  'NOS':recordData[3],
                  'PROC':recordData[4],
                  'MODS':'',
                  'BILLED AMOUNT':recordData[5],
                  'ALLOWED AMOUNT':recordData[6],
                  'DEDUCTED AMOUNT':recordData[7],
                  'COINS':recordData[8]+' '+recordData[9],
                  'GRP/RC AMOUNT':recordData[10],
                  'PROV PD':recordData[11]
               }
         RecordDetails.append(entry)
      elif len(recordData)==2:
         entry={
                  'PERF PROV':'',
                  'SERV DATE':'',
                  'POS':'',
                  'NOS':'',
                  'PROC':'',
                  'MODS':'',
                  'BILLED AMOUNT':'',
                  'ALLOWED AMOUNT':'',
                  'DEDUCTED AMOUNT':'',
                  'COINS':recordData[0],
                  'GRP/RC AMOUNT':recordData[1],
                  'PROV PD':''
               }
         RecordDetails.append(entry)
      elif len(recordData)==13:
         entry={
                  'PERF PROV':recordData[0],
                  'SERV DATE':DateTimeFormating(recordData[1]),
                  'POS':recordData[2],
                  'NOS':recordData[3],
                  'PROC':recordData[4],
                  'MODS':recordData[5],
                  'BILLED AMOUNT':recordData[6],
                  'ALLOWED AMOUNT':recordData[7],
                  'DEDUCTED AMOUNT':recordData[8],
                  'COINS':recordData[9]+' '+recordData[10],
                  'GRP/RC AMOUNT':recordData[11],
                  'PROV PD':recordData[12]
               }
         RecordDetails.append(entry)
      return RecordDetails
   
def getTotalClaim(claimLine,netDetails):
      #total claim details
      claimTotal=claimLine.split()
      claimTotalDetails={
         'PT RESP':claimTotal[2],
         'Billed Amount':claimTotal[5],
         'ALLOWED Amount':claimTotal[6],
         'DEDUCTED Amount':claimTotal[7],
         'COINS':claimTotal[8],
         'GRP/RC Amount':claimTotal[9],
         'PROV PD':claimTotal[10]
      }
      Net=netDetails.split()[-1]
      return claimTotalDetails,Net
 
def run_RemitiveAdvice(page):
   pagestext=getText(page)
   #partition tabular data
   tab_data=pagestext.split("____________________________________________________________________________________________________________________")
   cleaned_tabData=[data for data in tab_data if 'PERF PROV  SERV DATE' not in data]
   final_list=[]
   for i in range(len(cleaned_tabData)-1):
      all_details={}
      data=cleaned_tabData[i]
      lines=data.strip().split('\n')
      headers=lines[0]
      record_columns=lines[1:-2]
      claim_totalLines=lines[-2]
      netDetails=lines[-1] 
      
      #calling all function
      HeaderDetails=get_HeaderDetails(headers)
      RecordDetails=GetTabDetails(record_columns)
      claimTotalDetails,Net=getTotalClaim(claim_totalLines,netDetails)

      
      
      all_details['Header Details']=HeaderDetails
      all_details['ClaimDetails']=RecordDetails
      all_details['Claim Total Details']=claimTotalDetails
      all_details['NET']=Net
      final_list.append(all_details)
   return final_list


pdfPath="C:\\Users\\ankitha\\Downloads\\815817296_04.17.2024_$20321.43-(99 pages  have on testing do not touch).pdf"
reader=PdfReader(pdfPath)
pages=reader.pages
res=run_RemitiveAdvice(pages)
print(res)