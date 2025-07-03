import subprocess
import json
import logging
from database.db_config import requests_collection,clients_collection

def generate_email(client_id):
    #Uses the Mistral model (via Ollama) to generate an audit request email.
    #Retrieves request details dynamically from MongoDB.


    try:
        # Fetch request details from MongoDB
        request_data = requests_collection.find_one({"client_id": str(client_id)})
        client_related_data=clients_collection.find_one({"client_id":str(client_id)})

        if not request_data:
            logging.error(f"No request found for client_id: {client_id}")
            return {"error": "No audit request found"}

        # Extracting client details
        client_name = request_data.get('name', 'Client')
        company_name = request_data.get('company_name', 'Your Company')  # Ensure correct key
        email = request_data.get('email', 'N/A')
        phone = request_data.get('phone', 'N/A')
        status = request_data.get('status', 'Pending')
        evidence_submitted = request_data.get('evidence_submitted', [])
        follow_ups = request_data.get('follow_ups', 0)
        deadline = request_data.get('deadline', 'No Deadline Provided')

        print("Request Data:",request_data)


        pending_documents = [
            doc['document'] for doc in request_data.get("evidence_required", []) if isinstance(doc, dict)
        ]
        pending_docs_str = ', '.join(pending_documents) if pending_documents else 'None'

        # Extract submitted documents correctly
        submitted_documents = [
            doc['document_name'] for doc in request_data.get("evidence_submitted", []) if isinstance(doc, dict)
        ]
        submitted_docs_str = ', '.join(submitted_documents) if submitted_documents else 'None'

        # Extract client name properly
        client_name = request_data.get('name', 'Valued Client')  
        company_name = client_related_data.get('company_name', 'Your Company')

        
        prompt = f"""
        Act as the KPMG Auditors Team and draft a professional HTML-formatted email to {client_name}, the representative of {company_name}.

        **Instructions:**
        - The email must use HTML formatting.
        - The subject should appear on a separate line in plain text using a <p><strong>...</strong></p> tag with no extra styling — it should not be blue or have a larger font size than the rest of the email body. Use: "Subject: Urgent: Audit Evidence Submission Reminder - KPMG Auditors"
        - The body should start with "Dear {client_name},".
        - List pending audit documents using <ul><li> format.
        - Emphasize the importance of submitting documents before the deadline: {deadline}.
        - Maintain a professional, firm tone.
        - Do not include any sender signature inside the body (we will add it ourselves).
        - Avoid phrases like "Best regards" or any footer lines.

        Here are the details:
        - Client Name: {client_name}
        - Company Name: {company_name}
        - Email: {email}
        - Phone: {phone}
        - Audit Status: {status}
        - Submitted Documents: {submitted_docs_str}
        - Pending Documents: {pending_docs_str}
        - Deadline: {deadline}
        - Follow-ups Sent: {follow_ups}
        """

        # Run the Ollama command correctly
        result = subprocess.run(
            ["ollama", "run", "mistral"],  # Run the model
            input=prompt,  # Pass prompt as input
            capture_output=True,
            text=True
        )

        print("Generaed Promp:\n", prompt)

        if result.returncode != 0:
            logging.error(f"Error running Ollama: {result.stderr}")
            return {"error": "Failed to generate email content"}

        # Return as dictionary instead of a raw string
        return {"email_body": result.stdout.strip()}
    
    except Exception as e:
        logging.error(f"Exception in generate_email: {e}")
        return {"error": "Error generating email content"}
