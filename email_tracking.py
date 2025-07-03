from datetime import datetime, timedelta
from database.db_config import email_tracking_collection, requests_collection, clients_collection
import sendgrid
import os
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from generate_email import generate_email

#Loading environment variables
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

if not SENDGRID_API_KEY:
    raise ValueError("Error: SENDGRID_API_KEY is missing from .env file.")
if not SENDER_EMAIL:
    raise ValueError("Error: SENDER_EMAIL is missing from .env file.")

sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)

def track_and_send_email(client_id):
    """Retrieve the generated email and send it via SendGrid"""

    # Cheking if an email was already sent in the last 24 hours
    last_email = email_tracking_collection.find_one(
        {"client_id": client_id},
        sort=[("timestamp", -1)]
    )
    
    if last_email:
        last_sent_time = last_email.get("timestamp")
        if last_sent_time and datetime.utcnow() - last_sent_time < timedelta(hours=24):
            return {"message": "Email already sent in the last 24 hours"}

    # Fetching request details 
    request = requests_collection.find_one({"client_id": client_id})
    if not request:
        return {"error": "No audit request found for this client"}

    #Fetching client email details
    client_email = request.get("email")
    company_name = request.get("company_name", "Your Company")
    status = request.get("status", "Pending")
    deadline = request.get("deadline", "No Deadline Specified")




    if not client_email:
        return {"error": "Client email not found"}
    
    client = clients_collection.find_one({"client_id": client_id})
    client_name = client.get("client_name", "Valued Client") if client else "Valued Client"

    #Generating email content
    email_response = generate_email(client_id)
    if "error" in email_response:
        return email_response

    email_body = email_response.get("email_body")
    subject = "Audit Evidence Submission Reminder"

    #Store email in tracking collection
    email_tracking_collection.insert_one({
        "client_id": client_id,
        "email_body": email_body,
        "timestamp": datetime.utcnow()
    })

    #Send the email
    return send_email(client_email, subject, client_name, company_name, status, deadline,email_body)

def send_email(client_email, subject, client_name, company_name, status, deadline, email_body):
    try:
        email = Mail(
            from_email=SENDER_EMAIL,
            to_emails=client_email,
            subject=subject,
            html_content=f"""
            <html>
                <body>
                    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">  

                        {email_body}

                        <br><br>
                        <p><strong>Best Regards,</strong><br>
                        KPMG Auditors Team</p>
                    </div>
                </body>
            </html>
            """
        )

        response = sg.send(email)
        return {"message": f"Email sent to {client_email} successfully", "status_code": response.status_code}

    except Exception as e:
        return {"error": f"Failed to send email to {client_email}: {str(e)}"}


def send_automatic_reminders():
    now = datetime.utcnow()

    pending_requests = requests_collection.find({"status": "Pending"})
    for request in pending_requests:
        client_id = request.get("client_id")
        client_email = request.get("email")
        if not client_email:
            continue

        # Checking if an email was already sent in the last 24 hours
        last_email = email_tracking_collection.find_one(
            {"client_id": client_id},
            sort=[("timestamp", -1)]
        )
        if last_email:
            last_sent_time = last_email.get("timestamp")
            if last_sent_time and now - last_sent_time < timedelta(hours=24):
                continue  
            # Skip sending email if the mail was already sent in last 24 hours

        # Generate and send reminder email
        email_response = generate_email(client_id)
        if "error" in email_response:
            continue
        email_body = email_response.get("email_body")
        subject = "Reminder: Audit Evidence Submission Due"
        send_email(client_email, subject, email_body)

    return {"message": "Reminder emails sent to all pending clients"}
