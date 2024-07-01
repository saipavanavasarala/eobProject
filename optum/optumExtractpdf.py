import PyPDF4 as p2 
import re
import pandas as pd 
#pdffile = open("C:\\Users\\ankitha\\Downloads\\ClaimEOPDetail_CCSCAN_2024_6_CROW-7.pdf","rb")
#pdfread=p2.PdfFileReader(pdffile)




def extract_between(text, start, end):
    parts = text.split(start)
    if len(parts) > 1:
        sub_parts = parts[1].split(end)
        if len(sub_parts) > 1:
            return sub_parts[0]
    return None
 
 
def getTabDetails(pdfread):
   recordDetails=[]
   
   NumOfPages=len(pdfread.pages)
   for i in range(NumOfPages):
      pageinfo= pdfread.pages[i]  #pdfread.getPage(i)
      text=pageinfo.extract_text()
      start_pattern='Cap Month:'
      end_pattern='Total RVU\n\nCoPay'
      pattern = re.compile(fr'{re.escape(start_pattern)}(.*?)({re.escape(end_pattern)})', re.DOTALL) 
      cleanedText=re.sub(pattern,"",text)  
      #print(cleanedText)
      pattern = re.compile(fr'([A-Z]+,\s+[A-Z]+\s+\(\S+\)|[A-Z]+\s+[A-Z]+,\s+[A-Z]+\s+\(\S+\)|[A-Z-]+,\s+[A-Z]+\s+\(\S+\)|[A-Z]+,[A-Z]+\s+\(\S+\)|[A-Z\s]+,\s+[A-Z]+\s+\(\S+\))', re.DOTALL)  
      data=pattern.findall(cleanedText)
      

      for j in range(len(data)-1):
         start_pattern=data[j]
         end_pattern=data[j+1]
   #         pattern = re.compile(fr'(?<={start_pattern})(.*?)({end_pattern})', re.DOTALL)
   #         tab_data=pattern.findall(cleanedText)
         name=" ".join(start_pattern.split()[:-1])
         memberId=start_pattern.split()[-1].replace("(","").replace(")","")
         tab_data = extract_between(cleanedText, start_pattern, end_pattern)
         tabDatalist=tab_data.split()
      
         if len(tabDatalist)==12:
               updatedList=[''.join(tabDatalist[:2]) + tabDatalist[2]]+tabDatalist[3:]
               updatedList.insert(6,'')   #mos
               updatedList.insert(5,'')  #dlag code 2
               updatedList.insert(0,f'{name}')
               updatedList.insert(1,f'{memberId}')
      #             print(updatedList)
      #             print(len(updatedList))

         elif len(tabDatalist)==13:
               updatedList=[''.join(tabDatalist[:2]) + tabDatalist[2]]+tabDatalist[3:]
               if len(updatedList[5])>2:
                  updatedList.insert(5,'')
               if len(updatedList[7])>2:
                  updatedList.insert(7,'')
               updatedList.insert(0,f'{name}')
               updatedList.insert(1,f'{memberId}')
         elif len(tabDatalist)==14:
               updatedList=[''.join(tabDatalist[:2]) + tabDatalist[2]]+tabDatalist[3:]
               updatedList.insert(0,f'{name}')
               updatedList.insert(1,f'{memberId}')
               
               
         elif len(tabDatalist)>14:
               #print(tabDatalist)
               indices=[index for index,value in enumerate(tabDatalist) if len(value)==20]
               records = [tabDatalist[indices[i]:indices[i+1]] for i in range(len(indices)-1)]
               records.append(tabDatalist[indices[-1]:])
   
               updatedList=[]
               for record in records:
                  if len(record)==12:
                     recordList=[''.join(record[:2]) + record[2]]+record[3:]
                     recordList.insert(6,'')   #mos
                     recordList.insert(5,'')  #dlag code 2
                     recordList.insert(0,f'{name}')
                     recordList.insert(1,f'{memberId}')

                  elif len(record)==13:
                     recordList=[''.join(record[:2]) + record[2]]+record[3:]
                     if len(recordList[5])>2:
                           recordList.insert(5,'')
                     if len(recordList[7])>2:
                           recordList.insert(7,'')
                     recordList.insert(0,f'{name}')
                     recordList.insert(1,f'{memberId}')
                  elif len(record)==14:
                     recordList=[''.join(record[:2]) + record[2]]+record[3:]
                     recordList.insert(0,f'{name}')
                     recordList.insert(1,f'{memberId}')
                  
                  updatedList.append(recordList)
                     
         recordDetails.append(updatedList)  
   final_list=[]
   for record in recordDetails:
      if len(record)<14:
         for rows in record:
               final_list.append(rows)
      else:
         final_list.append(record)
   for index,data in enumerate(final_list):
    if len(data)==15:
        final_list.remove(final_list[index])
   
   HeaderKeys=['Member','MemberId','Claim/Line','Prov ClaimId','POS','DOS','Dlag Code','Dlag Code2','Service Code','Mod','Quantity','Revenue','Total Revenue','CoPay']

   df = pd.DataFrame(final_list, columns=HeaderKeys)
   return df


# pdffile = open("C:\\Users\\ankitha\\Downloads\\ClaimEOPDetail_CCSCAN_2024_6_CROW-7.pdf","rb")
# pdfread=p2.PdfFileReader(pdffile)    
# res=getTabDetails(pdfread)
# print(res)