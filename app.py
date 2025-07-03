from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from generate_email import generate_email
from database.db_config import requests_collection,users_collection,clients_collection,get_client_details_from_db,evidence_collection
from routes.client_routes import client_bp
from routes.auditor_routes import auditor_bp
from routes.user_routes import user_bp
import bcrypt
from email_tracking import track_and_send_email,send_automatic_reminders
from flask_apscheduler import APScheduler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from bson import ObjectId

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

scheduler=APScheduler()

@scheduler.task("interval", hours=24)  
def scheduled_reminders():
    send_automatic_reminders()

scheduler.init_app(app)
scheduler.start()


# Function to hash passwords
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


app.register_blueprint(client_bp) 
app.register_blueprint(auditor_bp) 
app.register_blueprint(user_bp)

@app.route("/")
def home():
    return jsonify({"message": "Audit AI Agent API is running!"})

# Route to manually add an auditor
@app.route("/add_auditor", methods=["POST"])
def add_auditor():
    data = request.json
    auditor_id = data.get("id")
    password = data.get("password")

    if not auditor_id or not password:
        return jsonify({"error": "ID and password are required"}), 400

    # Check if auditor already exists
    if users_collection.find_one({"id": auditor_id}):
        return jsonify({"error": "Auditor already exists"}), 400

    # Hash password and insert into database
    hashed_password = hash_password(password)
    users_collection.insert_one({
        "id": auditor_id,
        "password": hashed_password,
        "role": "auditor"
    })

    return jsonify({"message": "Auditor added successfully"}), 201


logging.basicConfig(level=logging.INFO)




@app.route("/client/evidence/<client_id>", methods=["GET"])
def get_client_evidence(client_id):
    client_data = clients_collection.find_one({"client_id": client_id})

    if not client_data:
        return jsonify({"error": "Client not found"}), 404

    required_evidence = client_data.get("required_evidence", [])

    submitted_evidence = list(evidence_collection.find({"client_id": client_id}, {"_id": 0}))

    for evidence in submitted_evidence:
        filename = evidence.get("filename")  
        if filename:
            file_path = os.path.abspath(f"uploads/{filename}")
            print(f"Checking file: {file_path}")  

            try:
                with open(file_path, "rb") as f:
                    evidence["file_data"] = f.read()
            except FileNotFoundError:
                print(f"❌ File not found: {file_path}")
                evidence["file_data"] = None 
        else:
            print(f"⚠️ Warning: Missing filename in evidence: {evidence}") 
            evidence["file_data"] = None 

    return jsonify({
        "required_evidence": required_evidence,
        "evidence_submitted": submitted_evidence
    })


@app.route("/get_requests", methods=["GET"])
def get_requests():
    
    requests_list = list(requests_collection.find({}))
    for req in requests_list:
        req["_id"] = str(req["_id"])
    return jsonify(requests_list)


def serialize_document(doc):
    """Convert MongoDB document to JSON-serializable format."""
    doc["_id"] = str(doc["_id"]) 
    return doc

@app.route("/audit_requests/<client_id>", methods=["GET"])
def get_audit_request(client_id):
    """Check if there is an audit request for a given client ID."""
    audit_request = requests_collection.find_one({"client_id": client_id})
    if audit_request:
        return jsonify({"exists": True, "audit_request": serialize_document(audit_request)}), 200
    else:
        return jsonify({"exists": False}), 200



# Send email for pending requests manually
@app.route("/send_email", methods=["POST"])
def send_email():
    try:
        data = request.get_json()
        if not data or "client_id" not in data:
            return jsonify({"error": "Invalid request, client_id missing"}), 400

        client_id = str(data["client_id"])
        send_result = track_and_send_email(client_id)
        if "error" in send_result:
            return jsonify(send_result), 400

        return jsonify(send_result), 200

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# Triggering automatic reminders manually
@app.route("/send_reminders", methods=["POST"])
def send_reminders():
    return jsonify(send_automatic_reminders())


if __name__ == "__main__":
    app.run(debug=True)



