import re,json
from datetime import datetime
from pdf2image import convert_from_path
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
poppler_path = r"C:\\Program Files\\poppler-0.68.0\\bin"

def DateTimeFormating(date_str):
    # Parse the string into the desired format
    date_obj = datetime.strptime(date_str, '%m%d%y')
    # Format the date object into 'month date year' format
    formatted_date = date_obj.strftime('%Y-%m-%d')
    return formatted_date

def intializeModel():
    model = ocr_predictor('db_resnet50', 'crnn_vgg16_bn', pretrained=True)
    return model
def process_image(image):
    model=intializeModel()
    return model([image])


def extract_text(pdfPath):
    pil_images = convert_from_path(pdfPath, poppler_path=poppler_path)

    # Downscale and convert PIL images to NumPy arrays
    resized_images = [image.resize((image.width // 2, image.height // 2)) for image in pil_images]
    numpy_images = [np.array(image) for image in resized_images]

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_image, numpy_images))
    final_result = results  
    return final_result

def PreprocessText(pdfPath):
    ExtractedText=extract_text(pdfPath)
    all_text=""
    for res in ExtractedText:
        for document in res.export()['pages']:
            for block in document['blocks']:

                for line in block['lines']:
                    line_text=""
                    for word in line['words']:
                        line_text=line_text+" "+word['value']
                    all_text=all_text+"\n"+line_text
    return all_text
                    

def get_all_record(PdfPath):
    all_text=PreprocessText(PdfPath)
    individual_text = re.findall(r"NAME(.*?NET\s*[0-9]+\.[0-9]+)", all_text, re.DOTALL)
    TabHeaderKeys=['PERF PROV','Service Date','POS','NOS','PROC','MODS','Billed Amount','Allowed Amount','DEDUCT Amount','COINS1','GRP/RC Amount1','PROV PD','COINS2','GRP/RC Amount2']
    claimTotalHeaderKeys=['Billed Amount','Allowed Amount','Deduct Amount','Coins','GRP/RC Amount','Prov PD']
    AllDetails=[]
    for text in individual_text:
        AllRecord={}
        cleanedText=text.replace("\n"," ") #REMOVE /n
        name=re.findall("(.*)MID",cleanedText)[0].strip()
        Mid=re.findall("(?<=MID)(.*)(ACNT)",cleanedText)[0]
        if "_" in Mid:
            Mid.remove("_")
        Mid = Mid[0]

        Acnt=re.findall("(?<=ACNT)(.*)(ICN)",cleanedText)[0][0].strip()
        Icn=re.findall("(?<=ICN)(.*)(ASG)",cleanedText)[0][0].strip()
        Asg=re.findall(r"([yY.] MOA MA\d{2}(?: MA\d{2})?)",cleanedText)
        if Asg:
            Asg=Asg[0]
        tabData=re.findall(r"(\d{4}\s+\d{6}|\d{4}.\s+\d{6})(.*)(PT RESP|PT. RESP)",cleanedText)
    
        if tabData:
            tabData=tabData[0][0]+" "+tabData[0][1]
            TabRecordPattern=r"(\d{4}\s+\d{6}|\d{4}.\s+\d{6}|\d{4}\s+\d+/\d+)"
            TabRecords= re.split(TabRecordPattern,tabData)[1:]
            
            _Tabrecords = [TabRecords[i] + " " + TabRecords[i+1] for i in range(0, len(TabRecords), 2)]

            TabDetails=[]
            for lines in _Tabrecords:
                Tab_elments=lines.split()
            

                if len(Tab_elments)==14:
                    Tab_elments[8]=Tab_elments[8]+" "+Tab_elments[9]
                    Tab_elments.remove(Tab_elments[9])
                    Tab_elments.insert(5,"")

                elif len(Tab_elments)==11:
                    if len(Tab_elments[3])!=3:
                        Tab_elments.insert(3,"")
                    Tab_elments[8]=Tab_elments[8]+" "+Tab_elments[9]
                    Tab_elments.remove(Tab_elments[9])
                    Tab_elments.insert(5,"")
                    Tab_elments.insert(13,"")
                    Tab_elments.insert(14,"")
                    
                elif len(Tab_elments)==12:
                    Tab_elments[8]=Tab_elments[8]+" "+Tab_elments[9]
                    Tab_elments.remove(Tab_elments[9])
                    Tab_elments.insert(5,"")
                    Tab_elments.insert(13,"")
                    Tab_elments.insert(14,"")
        
                elif len(Tab_elments)==13:
                    if len(Tab_elments[5])!=2:
                        Tab_elments.insert(5,"")
                    Tab_elments[9]=Tab_elments[9]+" "+Tab_elments[10]
                    Tab_elments.remove(Tab_elments[10])

                    if len(Tab_elments)==12:
                        Tab_elments.insert(13,"")
                        Tab_elments.insert(14,"")
                    elif len(Tab_elments)==13:
                        Tab_elments.insert(10,"")
                elif len(Tab_elments)==15:
                    if "REM:" in Tab_elments:
                        Tab_elments.remove(Tab_elments[-1])
                        Tab_elments.remove(Tab_elments[-1])
                        if len(Tab_elments[5])!=2:
                            Tab_elments.insert(5,"")
                            Tab_elments.remove(Tab_elments[-1])
                        Tab_elments[9]=Tab_elments[9]+" "+Tab_elments[10]
                        Tab_elments.remove(Tab_elments[10])
                        Tab_elments.insert(13,"")
                        Tab_elments.insert(14,"")
                    else:
                        Tab_elments[9]=Tab_elments[9]+" "+Tab_elments[10]
                        Tab_elments.remove(Tab_elments[10])
                    

                elif len(Tab_elments)==18:
                    Tab_elments=Tab_elments[:16]
                    Tab_elments[8]=Tab_elments[8]+" "+Tab_elments[9]
                    Tab_elments.remove(Tab_elments[9])
                    Tab_elments.remove(Tab_elments[11])
                    Tab_elments.remove(Tab_elments[11])
                    Tab_elments.insert(5,"")

                
                elif len(Tab_elments)==16:
                    Tab_elments=Tab_elments[:13]
                    Tab_elments[8]=Tab_elments[8]+" "+Tab_elments[9]
                    Tab_elments.remove(Tab_elments[9])
                    Tab_elments.insert(12,"")
                    Tab_elments.insert(13,"")
                    
                if len(Tab_elments)==14:
                    TabDetails.append(dict(zip(TabHeaderKeys,Tab_elments)))
        
            PtResp=re.findall(r"(PT RESP|PT. RESP)(.*)(CLAIM TOTALS)",cleanedText)
            if PtResp:
                PtResp=PtResp[0][1].strip()
            else:
                PtResp=""
            claimTotal=re.findall("(?<=CLAIM TOTALS)(.*)(NET)",cleanedText)[0][0]
            Element_claimTotal=claimTotal.split()[:6]
            ClaimTotalDetails=dict(zip(claimTotalHeaderKeys,Element_claimTotal))
            
            NetAmt=re.findall("(?<=NET )(.*)",cleanedText)[0].strip()
            AllRecord['NAME']=name
            AllRecord['MID']=Mid
            AllRecord['Account']=Acnt
            AllRecord['ICN']=Icn
            AllRecord['ASG']=Asg
            AllRecord['Table Details']=TabDetails
            AllRecord['PT RESP']=PtResp
            AllRecord['CLAIM Total']=ClaimTotalDetails
            AllRecord['NET']=NetAmt
            

            AllDetails.append(AllRecord)
    return json.dumps(AllDetails,indent=3)



pdfPath = r"D:\\New folder (4)\\Check#808909030 Date 03052024.pdf"
res=get_all_record(pdfPath)
print(res)