import streamlit as st
from pymongo import MongoClient
import time
import requests

# --- Connect to MongoDB ---
client = MongoClient("mongodb://localhost:27018/")
db = client["audit"]
evidence_collection = db["evidence"]

BASE_URL = "http://127.0.0.1:5000"  # Flask backend URL

st.title("Auditor Dashboard - Real-Time Evidence Tracking")

st.write("Select a client to view their submitted evidence.")

# --- Fetch All Clients with Evidence ---
def get_all_clients():
    return evidence_collection.distinct("client_id")

# --- Fetch Evidence for Selected Client ---
def get_client_evidence(client_id):
    evidence_list = evidence_collection.find({"client_id": client_id}, {"document_name": 1, "filename": 1})
    return list(evidence_list)

# --- Download Evidence ---
def download_evidence(client_id, filename):
    url = f"{BASE_URL}/auditor/download_evidence/{client_id}/{filename}"
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        st.success(f"Downloaded {filename} successfully!")
    else:
        st.error("Failed to download evidence.")

# --- UI Elements ---
clients = get_all_clients()

if not clients:
    st.warning("No clients have submitted evidence yet.")
else:
    selected_client = st.selectbox("Select a Client", clients)

    if selected_client:
        st.subheader(f"Evidence Submitted by {selected_client}")

        evidence_list = get_client_evidence(selected_client)

        if not evidence_list:
            st.warning("No evidence submitted yet.")
        else:
            for evidence in evidence_list:
                col1, col2 = st.columns([3, 1])
                col1.write(f"📄 {evidence['document_name']} - {evidence['filename']}")
                if col2.button(f"Download {evidence['filename']}", key=evidence["filename"]):
                    download_evidence(selected_client, evidence["filename"])

# --- Real-Time Evidence Tracking ---
st.write("Listening for new submissions...")

with evidence_collection.watch() as stream:
    for change in stream:
        st.experimental_rerun()  # Refresh UI when new evidence is added
