import requests

BASE_URL = "http://127.0.0.1:5000"  # Flask API URL

# Login API
def login(id, password, role):
    url = f"{BASE_URL}/login"
    data = {"id": id, "password": password, "role": role}
    response = requests.post(url, json=data)
    print("Raw Response: ",response.text)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return {"error": "Invalid response from server"}
    
def check_audit_request(client_id):
    
    response = requests.get(f"{BASE_URL}/audit_requests/{client_id}")
    return response.json()  # Returns audit request data


import requests

def register_client(client_id, company_name, phone, email, address, password, retype_password):
    if password != retype_password:
        return {"error": "Passwords do not match"}

    url = f"{BASE_URL}/client/register"
    data = {
        "client_id": client_id,
        "company_name": company_name,
        "phone": phone,
        "email": email,
        "address": address,
        "password": password,
        "retype_password": retype_password
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"HTTP request failed: {str(e)}"}
    except ValueError:
        return {"error": "Invalid JSON response from the server"}



def get_client_evidence(client_id):
    url = f"{BASE_URL}/client/evidence/{client_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Server error: {str(e)}"}


def upload_evidence(client_id, file, document_name):
    url = f"{BASE_URL}/client/submit_evidence"
    
    files = {"evidence": (file.name, file, "application/pdf")}
    data = {"client_id": client_id, "document_name": document_name}
    
    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Server error: {str(e)}"}

def create_audit_request(data):
    url = f"{BASE_URL}/create_audit_request"
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Server error: {str(e)}"}


def get_auditor_dashboard(auditor_id):
    url = f"{BASE_URL}/auditor/dashboard?auditor_id={auditor_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Server error: {str(e)}"}

def download_evidence(client_id, filename):
    url = f"{BASE_URL}/auditor/download_evidence/{client_id}/{filename}"
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        return {"message": f"Downloaded {filename} successfully!"}
    
    return {"error": "Failed to download evidence"}


def send_reminder(client_id):
    url = f"{BASE_URL}/audit/send_reminder"
    data = {"client_id": client_id}
    
    response = requests.post(url, json=data)
    
    try:
        return response.json()
    except Exception:
        return {"error": "Invalid server response"}

def track_and_send_email(client_id):
    response = requests.post(f"{BASE_URL}/send-follow-up-email", json={"client_id": client_id})
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to send email: {response.text}"}
