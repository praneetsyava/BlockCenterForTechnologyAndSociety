from flask import Flask, request, jsonify
import rpy2.robjects as robjects
from reportlab.pdfgen import canvas
from flask_cors import CORS
import ssl
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

app = Flask(__name__)
CORS(app)

def calculate_age_and_day_of_birth(dob):
    
    try:
        r = robjects.r

        # Load the R script
        r.source('/Users/praneetsy/Documents/RA/FirstAttempt/BlockCenterForTechnologyAndSociety/blockcenter/src/app/calculate_age.R')
        # Call the R function and retrieve the result
        r_function = r['calculate_age_and_day_of_birth']
        result = r_function(dob)
        print(result)
    except Exception as e:
        print(f"Error executing R code: {e}")
    
    
    # Extract age and day_of_week from the R result
    age = int(result.rx2('age')[0])
    day_of_week = str(result.rx2('day_of_week')[0])
    
    return age, day_of_week
   

def generate_pdf(first_name, last_name, age, day_of_week):
    # Generate PDF with person's information
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, f'Name: {first_name} {last_name}')
    c.drawString(100, 730, f'Age: {age}')
    c.drawString(100, 710, f'Day of Birth: {day_of_week}')
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

def send_email_with_pdf(email, pdf_buffer):
    
    # SMTP configuration and email sending
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = 'praneetsy@gmail.com'
    msg['To'] = email
    msg['Subject'] = 'Your PDF Document'

    # Attach the PDF to the email
    pdf_attachment = MIMEApplication(pdf_buffer.getvalue(), Name="result.pdf")
    pdf_attachment['Content-Disposition'] = f'attachment; filename="{pdf_attachment["Name"]}"'
    msg.attach(pdf_attachment)

    # Establish an SSL/TLS secured session with Gmail's SMTP server
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            # Login to the email server
            server.login('praneetsy@gmail.com', 'qmkr umur rndp fdkb')  # Use an App Password for security

            # Send the email
            server.sendmail(msg['From'], msg['To'], msg.as_string())
    except Exception as e:
        # Handle exceptions and errors
        print("exc", e)

@app.route('/process_form', methods=['POST'])
def process_form():
    try:
        # Get form data from the request
        data = request.get_json()
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        dob = data.get('dob')
        email = data.get('email')
        
        # Validate input (add more validation logic as needed)

        # Call embedded R code to calculate age and day of birth
        

        age, day_of_week = calculate_age_and_day_of_birth(dob)
        print("here", age)

        # Generate PDF
        pdf_buffer = generate_pdf(first_name, last_name, age, day_of_week)

        print("pdf", pdf_buffer)

        # Send email with PDF attachment
        send_email_with_pdf(email, pdf_buffer)

        return jsonify({"message": "Form processed successfully and email sent."})

    except Exception as e:
        # Handle exceptions and errors
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
