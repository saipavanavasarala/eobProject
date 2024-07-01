from .master import run_RemitiveAdvice
from io import BytesIO
import zipfile
import json

class MedicareEngine:

    def run(self,reader,pdfPath):
        data = run_RemitiveAdvice(reader)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            final_json=  json.dumps(data)
            json_bytes = final_json.encode('utf-8')
            zip_file.writestr(f"output.json", json_bytes)

        return zip_buffer