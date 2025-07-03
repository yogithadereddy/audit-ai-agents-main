from flask import Blueprint, request, jsonify,send_file
from models.auditor_model import create_audit_request, get_auditor_dashboard, get_client_status
from models.auditor_model import auditor_login
from database.db_config import users_collection,clients_collection,evidence_collection
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
import os 
import io

auditor_bp = Blueprint("auditor_bp", __name__)


@auditor_bp.route("/add_auditor", methods=["POST"])
def add_auditor():
    data = request.json
    auditor_id = data.get("id")
    password = data.get("password")

    if not auditor_id or not password:
        return jsonify({"error": "Auditor ID and password are required"}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    users_collection.insert_one({"id": auditor_id, "password": hashed_password, "role": "auditor"})

    return jsonify({"message": "Auditor added successfully"}), 201

@auditor_bp.route("/create_audit_request", methods=["POST"])
def create_audit_request_route():
    data = request.json 

    if not data:
        return jsonify({"error": "Invalid request, no data received"}), 400

    response = create_audit_request(data)
    status_code = 400 if "error" in response else 201
    return jsonify(response), status_code


@auditor_bp.route("/auditor/dashboard", methods=["GET"])
def get_auditor_dashboard_route():
    auditor_id = request.args.get("auditor_id") 

    # Check if the auditor_id is valid
    auditor = users_collection.find_one({"id": auditor_id, "role": "auditor"})
    if not auditor:
        return jsonify({"error": "Unauthorized"}), 403  # Only auditors can access

    response = get_auditor_dashboard()
    return jsonify(response), 200


@auditor_bp.route("/client_status/<client_id>", methods=["GET"])
def get_client_status_route(client_id):
    response = get_client_status(client_id)
    return jsonify(response), 200



@auditor_bp.route("/auditor/get_client_evidence/<client_id>", methods=["GET"])
def get_client_evidence(client_id):
    """Fetches all submitted evidence for a client."""
    evidence_list = evidence_collection.find({"client_id": client_id})

    evidence_data = []
    for evidence in evidence_list:
        evidence_data.append({
            "document_name": evidence["document_name"],
            "filename": evidence["filename"]
        })

    return jsonify({"client_id": client_id, "evidence": evidence_data})


