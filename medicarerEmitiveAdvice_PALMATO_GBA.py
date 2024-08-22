from pdf2image import convert_from_path
import pytesseract
import cv2,json,re
import numpy as np
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
poppler_path = r"C:\\Program Files\\poppler-0.68.0\\bin"


def extract_text(pdf_path):
    images = convert_from_path(pdfPath, dpi=300, poppler_path=poppler_path)
    config = ('-l eng --oem 1 --psm 6')
    all_text=""
    for i, image in enumerate(images):
        
        # Convert to OpenCV format
        open_cv_image = np.array(image)
        # Convert RGB to BGR for OpenCV
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)
        # Convert to grayscale
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        # Apply thresholding (Binarization)
        _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # OCR with Tesseract
        text = pytesseract.image_to_string(binary_image, config=config)
        all_text+=text
    return all_text


def DateTimeFormating(date_str):
    # Parse the string into the desired format
    date_obj = datetime.strptime(date_str, '%m%d%y')
    # Format the date object into 'month date year' format
    formatted_date = date_obj.strftime('%Y-%m-%d')
    return formatted_date

def get_allRecords(pdf_path):
    all_text=extract_text(pdf_path)
    Individual_Details=all_text.split('NAME')
    Individual_Details[-1]=Individual_Details[-1].split("TOTALS:")[0]
    recordDetails_HeaderKeys=['PERF PROV','Service Date','POS','NOS','PROS','MODS','Billed Amount','Allowed Amount','Deduct Amont','COINS','GRP/RC Amont','PROV PD']
    ClaimTotalHeaderKeys=['Billed Amount','Allowed Amount','Deduct Amount','COINS','GRP/RC Amount','PROV PD']
    
    allDetails=[]
    for details in Individual_Details[1:]:
        HeaderWithRecordDetails={}
        name=re.findall("(.+)MID",details)[0].strip()
        Mid=re.findall("(?<=MID)(.*)(ACNT)",details)[0][0].lstrip().split(" ")[0]
        Acnt=re.findall("(?<=ACNT)(.*)(ICN)",details)[0][0].strip().strip("_")
        Acnt="I" + Acnt[1:] if Acnt[0] != "I" else Acnt
        Asg=re.findall("(?<=ASG)(.*)",details)[0]
        ASG=Asg[:-1] + '1' if Asg.endswith('L') else Asg
        line_pattern=re.compile(r"\d{4}\s+\d{6}.*")
        record_line=re.findall(line_pattern,details)
        
        record_lines=[]
        for line in record_line[1:]:
            record_element=line.split()

            if len(record_element)==12:
                if not record_element[-3].lower().startswith("c"):
                    record_element[-3]="C"+record_element[-3]
                    
                record_element[-4]=record_element[-4]+" "+record_element[-3]
                record_element.remove(record_element[-3])
                record_element.insert(5,"")

                
            if len(record_element)==14:
                record_element.remove(record_element[-3])

            if len(record_element)==13:
                if not record_element[-3].lower().startswith("c"):
                    record_element[-3]="C"+record_element[-3]
                record_element[-4]=record_element[-4]+" "+record_element[-3]
                record_element.remove(record_element[-3])

            #remove extra charcter from RC amount
            char_to_replace={":":".","-":".","°":"."}
            if len(record_element)==12:
                for key,val in char_to_replace.items():
                    record_element[-2]=record_element[-2].replace(key,val)

                if record_element[1]:
                    record_element[1]=DateTimeFormating(record_element[1])

                record_lines.append(dict(zip(recordDetails_HeaderKeys,record_element)))
    

        PT_Resp=re.findall("(?<=PT RESP)(.*)(CLAIM TOTALS)",details)[0][0].strip()

        #claim Totals
        claim_totalLine=re.findall("(?<=CLAIM TOTALS)(.*)",details)[0]
        claim_totalElements=claim_totalLine.split()
        claimTotal=dict(zip(ClaimTotalHeaderKeys,claim_totalElements))
        Net_Amount=re.findall("(?<=NET)(.*)",details)[0].strip()
        if len(Net_Amount)>10:
            Net_Amount=""
        HeaderWithRecordDetails['NAME']=name
        HeaderWithRecordDetails['MID']=Mid
        HeaderWithRecordDetails['ACNT']=Acnt
        HeaderWithRecordDetails['ASG']=ASG
        HeaderWithRecordDetails['Record Details']=record_lines
        HeaderWithRecordDetails['PT RESP']=PT_Resp
        HeaderWithRecordDetails['CLAIM TOTALS']=claimTotal
        HeaderWithRecordDetails['NET']=Net_Amount

        allDetails.append(HeaderWithRecordDetails)
    return json.dumps(allDetails,indent=3)

pdfPath = r"D:\\New folder (4)\\Check#808909030 Date 03052024.pdf"
res=get_allRecords(pdfPath)
print(res)