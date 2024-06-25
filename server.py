from flask import Flask,render_template,request,send_file
from flask_cors import CORS
import json
from PyPDF2 import PdfReader

from medicare import run_crossover,run_claim_adjustments,run_claim_denied,run_claim_paid,medicareEngine
from wellpoint import wEngine
from bcbs import BcbsEngine

import zipfile
from io import BytesIO
import os

#creating app    
# adding code for merger from testBranch
app = Flask(__name__)

@app.route("/",methods=["POST","GET"])
def index():
    if request.method == "GET":
        print("hit get method")
        return render_template("index.html")  
    
    if request.method == "POST":
        filee = request.files['file']
        data = request.form.get('organization')

        print(data)
        #return render_template('index.html')
        #print("The file name is : ",filee.filename)
        pdfPath = f"./pdfs/{filee.filename}"
        filee.save(pdfPath)
        reader = PdfReader(pdfPath)

        zip_buffer = BytesIO()
        if data=='medicare':
            zip_buffer = medicareEngine(reader)
            zip_buffer.seek(0)
        elif data=='wellpoint ERA':
            zip_buffer = wEngine(reader)
            zip_buffer.seek(0)
        elif data=="bcbs":
            engine = BcbsEngine()
            zip_buffer = engine.run(reader,pdfPath)
            zip_buffer.seek(0)
            print("The zip buffer is : ")
        

        
    
        os.remove(pdfPath)
        return send_file(zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{filee.filename.replace(".pdf","")}.zip') 
         




        #return render_template("index.html") 


if __name__ =="__main__":
    app.run(debug=True,host="192.168.8.173")