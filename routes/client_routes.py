from flask import Blueprint, request, jsonify
from models.client_model import register_client, client_login
from database.db_config import company_clients_collection,requests_collection,users_collection,evidence_collection 
import os
import io
from bson.binary import Binary


UPLOAD_FOLDER="uploads"
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

client_bp = Blueprint("client_bp", __name__)

@client_bp.route("/client/register", methods=["POST"])
def register_client_route():
    try:
        data = request.json
        response = register_client(data)
        status_code = 400 if "error" in response else 201
        return jsonify(response), status_code
    except Exception as e:
        # Log this in production
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@client_bp.route("/login", methods=["POST"])
def client_login_route():
    data = request.json
    role = data.get("role")  # Get role from request

    if not role:
        return jsonify({"error": "Role is required"}), 400

    print("Login Data Received:", data)  # Debugging

    if role == "client":
        if not data.get("id") or not data.get("password"):  # Ensure both fields are present
            return jsonify({"error": "ID and password are required"}), 400

        response, status_code = client_login(data)  # ✅ Fix: Ensure tuple is unpacked
        print("Login Response:", response)  # Debugging
        return jsonify(response), status_code

    elif role == "auditor":
        from models.auditor_model import auditor_login
        auditor_id = data.get("id")
        password = data.get("password")

        if not auditor_id or not password:
            return jsonify({"error": "ID and password are required"}), 400

        response, status_code = auditor_login(auditor_id, password)
        return jsonify(response), status_code

    else:
        return jsonify({"error": "Invalid role"}), 400


@client_bp.route("/client/evidence/<client_id>", methods=["GET"])
def get_client_evidence(client_id):
    """Fetch required evidence for the given client ID."""
    audit_request = requests_collection.find_one({"client_id": client_id}, {"_id": 0, "evidence_required": 1, "evidence_submitted": 1})

    if not audit_request:
        return jsonify({"error": "No audit requests"}), 404

    # Ensure evidence_required is extracted correctly
    evidence_required = [doc["document"] for doc in audit_request.get("evidence_required", [])]
    evidence_submitted = audit_request.get("evidence_submitted", [])

    return jsonify({
        "evidence_required": evidence_required,
        "evidence_submitted": evidence_submitted
    })


@client_bp.route("/client/submit_evidence", methods=["POST"])
def submit_evidence_route():
    """Handles client PDF uploads and stores them in MongoDB."""
    client_id = request.form.get("client_id")
    document_name = request.form.get("document_name")  

    if not client_id or not document_name:
        return jsonify({"error": "Client ID and document name are required"}), 400
    
    if "evidence" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["evidence"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Convert file to binary and store in MongoDB
    file_data = Binary(file.read())
    evidence_doc = {
        "client_id": client_id,
        "document_name": document_name,
        "filename": file.filename,
        "file_data": file_data,
        "status": "Submitted"
    }
    evidence_collection.insert_one(evidence_doc)

    # Update audit_requests collection with submitted evidence
    requests_collection.update_one(
        {"client_id": client_id, "status": {"$in": ["Pending", "In Progress"]}},
        {"$push": {"evidence_submitted": {"document_name": document_name, "filename": file.filename, "status": "Submitted"}}}
    )

    return jsonify({"message": f"{document_name} uploaded successfully!"}), 200

# New route for adding company clients
@client_bp.route("/company_clients/add", methods=["POST"])
def add_company_client():
    """Add a new company client (client_id + company_name)."""

    data = request.json

    if not data.get("client_id") or not data.get("company_name"):
        return jsonify({"error": "client_id and company_name are required"}), 400

    # Check if client_id already exists
    if company_clients_collection.find_one({"client_id": data["client_id"]}):
        return jsonify({"error": "Client ID already exists in company_clients"}), 400

    # Insert into MongoDB
    company_clients_collection.insert_one({
        "client_id": data["client_id"],
        "company_name": data["company_name"]
    })

    return jsonify({"message": "Company client added successfully"}), 201
