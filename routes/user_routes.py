from flask import Blueprint, request, jsonify
from database.db_config import users_collection

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/user/add", methods=["POST"])
def add_user():
    data = request.json

    if not data.get("client_id") or not data.get("password") or not data.get("role"):
        return jsonify({"error": "Missing required fields"}), 400

    if users_collection.find_one({"client_id": data["client_id"]}):
        return jsonify({"error": "Client ID already exists"}), 400

    users_collection.insert_one({
        "client_id": data["client_id"],
        "password": data["password"],
        "role": data["role"]
    })

    return jsonify({"message": "User added successfully"}), 201
