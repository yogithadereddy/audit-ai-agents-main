import streamlit as st
import os
import base64

# Load style.css from parent directory (frontend)
css_path = os.path.join(os.path.dirname(__file__), '..', 'styles.css')
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64_image("/Users/kdnai_dyogitha/Documents/PROJECTS/PROJECT-1/audit-ai-agents-main/frontend/pages/logo.png")


st.markdown(
    f"""
    <style>
        

        /* Sidebar base styling */
        [data-testid="stSidebar"] {{
            background-color: #00338D !important;
            padding-top: 0px !important;
        }}

        /* Sidebar logo at top */
        [data-testid="stSidebar"]::before {{
            content: "";
            display: block;
            background-image: url("data:image/png;base64,{logo_base64}");
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
            height: 100px;
            margin-bottom: 0px;
        }}

        /* Move sidebar content just below logo (targeting internal container) */
        [data-testid="stSidebar"] > div > div {{
            margin-top: 0px !important;
            padding-top: 0px !important;
        }}
    </style>

    <header></header>
    """,
    unsafe_allow_html=True
)

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from api import upload_evidence, get_client_evidence, check_audit_request
from database.db_config import requests_collection


st.title("Client Dashboard - Submit Evidence")

client_id = st.session_state.get("user_id")
user_role = st.session_state.get("role")

if not client_id:
    st.error("Please log in first.")
    st.stop()

if user_role != "client":
    st.error("Unauthorized access! Auditors cannot access this page.")
    st.stop()

if st.button("Logout"):
    st.session_state.clear()
    st.success("Logged out successfully! Redirecting to login page...")
    st.rerun()

#Checking if audit request exists
audit_request = check_audit_request(client_id)

if not audit_request.get("exists", False):  
    st.warning("No audit request found for your account. You will be notified when an audit is assigned.")
    st.stop()

#Fetch previously uploaded documents from MongoDB
uploaded_documents = get_client_evidence(client_id)
submitted_files = {doc["document_name"]: doc for doc in uploaded_documents.get("evidence_submitted", [])}

request_data = requests_collection.find_one({"client_id": str(client_id)})
evidence_required = request_data.get("evidence_required", [])

# Display the required documents
required_documents= [doc['document'] for doc in evidence_required if isinstance(doc, dict)]



st.subheader("Required Documents")


for index, doc in enumerate(required_documents):
    col1, col2, col3 = st.columns([3, 3, 2]) 

    col1.write(f"📄 **{doc}**") 
    
    unique_key = f"{client_id}_{index}"  

    if doc in submitted_files:
        col3.success("✅ Submitted") 
    else:
        file = col2.file_uploader(f"Upload {doc}", type=["pdf"], key=f"file_{unique_key}") 
        if file and col3.button(f"Submit {doc}", key=f"submit_{unique_key}"): 
            response = upload_evidence(client_id, file, doc)
            
            if "error" in response:
                st.error(response["error"])
            else:
                st.success(f"✅ {doc} submitted successfully!")
                st.rerun() 
