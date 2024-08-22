from .Bcbs import getAllData
import zipfile
from io import BytesIO
import json

class TennesseEngine:
    def run(self,reader,pdfPath):
        data = getAllData(pdfPath)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            final_json=  json.dumps(data)
            json_bytes = final_json.encode('utf-8')
            zip_file.writestr(f"output.json", json_bytes)

        return zip_buffer