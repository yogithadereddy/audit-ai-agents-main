from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Loading the environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
print("URL",MONGO_URI)
client = MongoClient(MONGO_URI)
db = client["audit"]

users_collection=db["users"]

company_clients_collection=db["company_clients"]

clients_collection = db["clients"]
#client information of clients after successful registration

requests_collection = db["audit_requests"]
#stores audit requests and their status

email_tracking_collection = db["email_tracking"]
#details of sent eails,tracking whether clients received and responded to them

evidence_collection=db["evidence"]
#for storing the evidence of the clients


def get_client_details_from_db(client_id):
    client_data = clients_collection.find_one({"client_id": client_id}, {"_id": 0, "email": 1, "company_name": 1})
    return client_data


  