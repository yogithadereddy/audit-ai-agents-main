from flask import jsonify
from werkzeug.utils import secure_filename
from database.db_config import users_collection, requests_collection, clients_collection, company_clients_collection
import os
from werkzeug.security import generate_password_hash,check_password_hash
import bcrypt
from database.db_config import company_clients_collection, clients_collection, users_collection
from werkzeug.security import generate_password_hash



def client_login(data):
    client_id = data.get("id")  
    password = data.get("password")

    if not client_id or not password:
        return {"error": "Client ID and password are required"}, 400

    user = users_collection.find_one({"id": client_id}) 

    if not user:
        return {"error": "Invalid credentials"}, 401

    if not check_password_hash(user["password"], password):
        return {"error": "Invalid credentials"}, 401

    return {"message": "Login successful", "role": user["role"]}, 200


def register_client(data):
    """Registers a client only if their client_id exists in company_clients."""

    try:
        print("[DEBUG] Validating required fields")
        required_fields = ["client_id", "company_name", "phone", "email", "address", "password", "retype_password"]
        if not all(field in data and data[field] for field in required_fields):
            return {"error": "Missing required fields"}

        if data["password"] != data["retype_password"]:
            return {"error": "Passwords do not match"}

        client_id = data["client_id"]
        print("[DEBUG] Checking if client exists in company_clients")
        existing_company_client = company_clients_collection.find_one({"client_id": client_id})
        if not existing_company_client:
            return {"error": "Invalid client ID. You must be a company client to register"}

        print("[DEBUG] Checking if already registered in users")
        if users_collection.find_one({"id": client_id}):
            return {"error": "Client ID already registered"}

        print("[DEBUG] Hashing password")
        hashed_password = generate_password_hash(data["password"], method='pbkdf2:sha256')


        new_client = {
            "client_id": client_id,
            "company_name": data["company_name"],
            "phone": data["phone"],
            "email": data["email"],
            "address": data["address"],
            "password": hashed_password 
        }

        print("[DEBUG] Inserting into clients_collection")
        clients_collection.insert_one(new_client)

        user_entry = {
            "id": client_id,
            "password": hashed_password, 
            "role": "client"
        }

        print("[DEBUG] Inserting into users_collection")
        users_collection.insert_one(user_entry)

        print("[DEBUG] Registration successful")
        return {"message": "Client registered successfully"}
    
    except Exception as e:
        import traceback
        print("[ERROR] Exception occurred in register_client:")
        traceback.print_exc()
        return {"error": f"Internal server error: {str(e)}"}

