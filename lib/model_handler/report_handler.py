from lib.models.report_model import PatientReportViewModel
from lib.extensions import mongo
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import io
class Report_handler:
    def __init__(self,uuid,disease):
        self.disease = disease
        self.uuid = uuid

    def report_generator(self):
        patient_data = mongo.db.patientdata.find_one({"uuid":self.uuid})
        current_date = datetime.today().strftime('%Y-%m-%d')
        report = PatientReportViewModel(self.uuid,patient_data['name'],patient_data['age'],patient_data['gender'],patient_data['email'],patient_data['phone'],patient_data['address'],self.disease,current_date).to_dict()
        return report
    
    def generate_pdf(self,patient_data):
        pdf_buffer = io.BytesIO()  # Create in-memory file
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

       
        c.setFont("Helvetica-Bold", 18)
        c.drawString(200, 750, "Hospital Medical Report")

    
        c.setStrokeColor(colors.black)
        c.setLineWidth(3)
        c.rect(50, 100, width - 100, height - 200)

     
        y = 650
        c.setFont("Helvetica-Bold", 14)
        for key, value in patient_data.items():
            c.drawString(70, y, f"{key}:")
            c.setFont("Helvetica", 12)
            c.drawString(200, y, str(value))  # Convert value to string
            c.setFont("Helvetica-Bold", 14)
            y -= 30

   
        c.setFont("Helvetica", 10)
        c.drawString(60, 50, f"Generated on: {patient_data['diagnosis_date']}")
        c.drawString(450, 50, "Authorized by XYZ Hospital")

        c.save()
        pdf_buffer.seek(0)  
        return pdf_buffer
        


