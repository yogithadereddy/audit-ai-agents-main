import bcrypt
from database.db_config import requests_collection, clients_collection,users_collection
from datetime import timedelta
from werkzeug.security import check_password_hash
from email_tracking import track_and_send_email

def auditor_login(auditor_id, password):
    auditor = users_collection.find_one({"id": auditor_id, "role": "auditor"})
    
    if not auditor:
        return {"error": "Auditor not found"}, 404

    if not check_password_hash(auditor["password"], password):
        return {"error": "Invalid password"}, 401

    return {"message": "Login successful"}, 200



def get_auditor_dashboard():
    dashboard = []
    
    requests = requests_collection.find({}, {"_id": 0})

    for request in requests:
        client = clients_collection.find_one({"client_id": request["client_id"]}, {"_id": 0, "name": 1, "company_name": 1})

        submitted_documents = set(request.get("submitted_documents", []))

        evidence_required_list = request.get("evidence_required", [])
        evidence_required = {doc["document"] for doc in evidence_required_list} 

        remaining_docs = list(evidence_required - submitted_documents)

        dashboard.append({
            "client_id": request["client_id"],
            "client_name": client.get("name", "Unknown") if client else "Unknown",
            "company_name": client.get("company_name", "Unknown") if client else "Unknown",
            "submitted_documents": list(submitted_documents),
            "pending_documents": remaining_docs,
            "status": request.get("status", "Pending"),
            "deadline": request.get("deadline", "No deadline set")
        })
    
    return dashboard


def get_client_status(client_id):
    request = requests_collection.find_one({"client_id": client_id}, {"_id": 0})

    if not request:
        return {"error": "No audit request found for this client"}

    submitted_documents = set(request.get("evidence_submitted", []))
    evidence_required = set(request.get("evidence_required", []))
    remaining_docs = list(evidence_required - submitted_documents)

    return {
        "client_id": client_id,
        "submitted_documents": list(submitted_documents),
        "pending_documents": remaining_docs,
        "status": request.get("status", "Pending"),
        "deadline": request.get("deadline", "No deadline set")
    }
def create_audit_request(data):
    required_fields = ["id", "email", "phone", "deadline", "evidence_required"]
    if not all(field in data and data[field] for field in required_fields):
        return {"error": "Missing or empty required fields"}

    client_exists = clients_collection.find_one({"client_id": data["id"]})
    if not client_exists:
        return {"error": "Client does not exist"}

    evidence_list = [{"document": doc} for doc in data["evidence_required"]]

    request_id = requests_collection.insert_one({
        "client_id": data["id"],
        "email": data["email"],
        "phone": data["phone"],
        "status": "Pending",
        "deadline": data["deadline"],
        "evidence_required": evidence_list,
        "evidence_submitted": [],
        "follow_ups": 0
    }).inserted_id

    email_response = track_and_send_email(data["id"])

    return {"message": "Audit request created", "id": str(request_id)}
