from .master import run_RemitiveAdvice
from io import BytesIO
import zipfile
import json
from .Medicare_Atena_extractPDF import getAllData

class MedicareEngine:

    def run(self,reader,pdfPath):
        data = run_RemitiveAdvice(reader)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            final_json=  json.dumps(data)
            json_bytes = final_json.encode('utf-8')
            zip_file.writestr(f"output.json", json_bytes)

        return zip_buffer
    
class MedicareAtenaEngine:

    def run(self,reader,pdfPath):
        data = getAllData(reader,pdfPath)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            final_json=  json.dumps(data)
            json_bytes = final_json.encode('utf-8')
            zip_file.writestr(f"output.json", json_bytes)

        return zip_buffer

