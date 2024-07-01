from .optumExtractpdf import getTabDetails
import pandas as pd

import io
from io import BytesIO
import zipfile


class OptumEngine:
    def run(self,reader,pdfPath):
        data =  getTabDetails(reader)

        csv_buffer = io.StringIO()
        data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

    # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr('data.csv', csv_buffer.getvalue())

        return zip_buffer