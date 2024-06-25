from medicare import run_crossover,run_claim_adjustments,run_claim_denied,run_claim_paid
import zipfile
from io import BytesIO
import json

def medicareEngine(reader):
        results = []
        results.append({"crossOver":run_crossover(reader)})
        results.append({"claimAdjustments":run_claim_adjustments(reader)})
        results.append({"claimDenied":run_claim_denied(reader)})
        results.append({"claimPaid":run_claim_paid(reader)})

        encodedString =[]
        
        for i in results:
            for key,value in i.items():
                temp = json.dumps(value)
                json_bytes = temp.encode('utf-8')
                encodedString.append({key:json_bytes})


        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            for row in encodedString:
                for key,json_bytes in row.items():
                    zip_file.writestr(f"{key}.json", json_bytes)

        return zip_buffer
