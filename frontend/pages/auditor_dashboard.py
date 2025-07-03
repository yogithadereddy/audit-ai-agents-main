# import streamlit as st

# # --- Must be the first Streamlit command ---
# st.set_page_config(page_title="Auditor Dashboard", page_icon="📊", layout="wide")

# import os
# from api import create_audit_request, get_auditor_dashboard, get_client_evidence
# import base64
# import plotly.express as px
# import pandas as pd

# # --- Load global CSS from style.css ---
# css_path = os.path.join(os.path.dirname(__file__), '..', 'styles.css')
# with open(css_path) as f:
#     st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
# from database.db_config import requests_collection


# if "role" not in st.session_state or "user_id" not in st.session_state:
#     st.error("Unauthorized access. Please log in.")
#     st.stop()

# auditor_id = st.session_state["user_id"]
# user_role = st.session_state["role"]

# # Restrict access to auditors only
# if user_role != "auditor":
#     st.error("Access Denied: Clients cannot view this page.")
#     st.stop()

# st.title("Auditor Dashboard - Client Overview")

# if st.button("Logout", key="logout_btn", help="Click to log out", use_container_width=True):
#     st.session_state.clear()
#     st.switch_page("pages/login.py")


# clients = get_auditor_dashboard(auditor_id)

# if clients and "error" not in clients:
#     # Extract Data for Visualization
#     client_ids = []
#     submitted_counts = []
#     pending_counts = []

#     for client in clients:
#         evidence_data = get_client_evidence(client["client_id"])
#         if evidence_data and "error" not in evidence_data:
#             total_required = len(evidence_data.get("evidence_required", []))
#             total_submitted = len(evidence_data.get("evidence_submitted", []))
#             pending = total_required - total_submitted

#             client_ids.append(client["client_id"])
#             submitted_counts.append(total_submitted)
#             pending_counts.append(pending)

#     # --- Create DataFrame for Visualization ---
#     import pandas as pd
#     df = pd.DataFrame({
#         "Client ID": client_ids,
#         "Submitted Evidence": submitted_counts,
#         "Pending Evidence": pending_counts
#     })

#     # --- Create a Stacked Bar Chart ---
#     fig = px.bar(
#         df, x="Client ID", y=["Submitted Evidence", "Pending Evidence"],
#         title="Client Evidence Submission Overview",
#         labels={"value": "Number of Evidences", "variable": "Status"},
#         barmode="stack"
#     )

#     fig.update_layout(xaxis=dict(type='category'))

#     # --- Display Chart in Streamlit ---
#     st.plotly_chart(fig, use_container_width=True)
# else:
#     st.warning("No clients found or error retrieving data.")


# clients = get_auditor_dashboard(auditor_id)

# if "error" in clients:
#     st.error(clients["error"])
# else:
#     st.subheader("Client Audit Status")
    
#     selected_client = st.selectbox("Select a Client to View Evidence", [c["client_id"] for c in clients])
    
    
    
#     if selected_client:
#         st.subheader(f"Submitted Evidence for Client {selected_client}")
        
#         evidence_list = get_client_evidence(selected_client)
#         #st.write("Debug: API Response for get_client_evidence", evidence_list)

#         if not evidence_list or "error" in evidence_list:
#             st.error(f"Failed to retrieve evidence: {evidence_list.get('error', 'Invalid server response')}")
#         else:
        
#             st.subheader("Required Evidence")
#             required_evidence = evidence_list.get("evidence_required", [])

#             if not required_evidence:
#                 st.warning("No required evidence listed for this client.")
#             else:
#                 for doc in required_evidence:
#                     st.write(f"🔵 {doc}")

#             st.subheader("Submitted Evidence")
#             submitted_evidence = evidence_list.get("evidence_submitted", [])

#             if not submitted_evidence:
#                 st.warning("No evidence submitted yet.")
#             else:
#                 for evidence in submitted_evidence:
#                     document_name = evidence.get("document_name")
#                     filename = evidence.get("filename")
#                     status = evidence.get("status")
                    
#                     if not all([document_name, filename, status]):
#                         st.error(f"Invalid evidence format: {evidence}")
#                         continue

#                     st.write(f"✅ {document_name} - {filename} ({status})")


# st.subheader("Create New Audit Request")
# with st.form(key="audit_request_form"):
#     client_id = st.text_input("Client ID", help="Enter the Client ID for the audit request")
#     email = st.text_input("Client Email", help="Enter the client's email")
#     phone = st.text_input("Client Phone", help="Enter the client's phone number")
#     deadline = st.date_input("Audit Deadline")

#     all_documents = [
#         "Balance Sheets", "Income Statements", "Cash Flow Statements",
#         "Bank Statements", "Invoices and Bills", "Tax Returns",
#         "Tax Registration Certificate", "Share Certificates"
#     ]
#     selected_documents = st.multiselect("Select Required Evidence Documents", all_documents)

#     submit_button = st.form_submit_button("Create Request")



# if submit_button:
#     if not client_id or not email or not phone or not selected_documents:
#         st.error("All fields are required!")
#     else:
#         request_data = {
#             "id": client_id,
#             "email": email,
#             "phone": phone,
#             "deadline": str(deadline),
#             "evidence_required": selected_documents
#         }
#         response = create_audit_request(request_data)

#         if "error" in response:
#             st.error(response["error"])
#         else:
#             st.success(f"Audit request created for Client {client_id}!")
#             st.success(f"Email sent successfully")


import streamlit as st
import base64

# --- Must be the first Streamlit command ---
st.set_page_config(page_title="Auditor Dashboard", page_icon="📊", layout="wide")

import os
from api import create_audit_request, get_auditor_dashboard, get_client_evidence
import base64
import plotly.express as px
import pandas as pd

# --- Load global CSS from style.css ---
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
from database.db_config import requests_collection

if "role" not in st.session_state or "user_id" not in st.session_state:
    st.error("Unauthorized access. Please log in.")
    st.stop()

auditor_id = st.session_state["user_id"]
user_role = st.session_state["role"]

# Restrict access to auditors only
if user_role != "auditor":
    st.error("Access Denied: Clients cannot view this page.")
    st.stop()

st.title("Auditor Dashboard - Client Overview")



clients = get_auditor_dashboard(auditor_id)

if clients and "error" not in clients:
    # Extract Data for Visualization
    client_ids = []
    submitted_counts = []
    pending_counts = []

    for client in clients:
        evidence_data = get_client_evidence(client["client_id"])
        if evidence_data and "error" not in evidence_data:
            total_required = len(evidence_data.get("evidence_required", []))
            total_submitted = len(evidence_data.get("evidence_submitted", []))
            pending = total_required - total_submitted

            client_ids.append(client["client_id"])
            submitted_counts.append(total_submitted)
            pending_counts.append(pending)

    # --- Create DataFrame for Visualization ---
    df = pd.DataFrame({
        "Client ID": client_ids,
        "Submitted Evidence": submitted_counts,
        "Pending Evidence": pending_counts
    })

    # --- Create a Stacked Bar Chart ---
    fig = px.bar(
        df, x="Client ID", y=["Submitted Evidence", "Pending Evidence"],
        title="Client Evidence Submission Overview",
        labels={"value": "Number of Evidences", "variable": "Status"},
        barmode="stack"
    )

    fig.update_layout(xaxis=dict(type='category'))

    # --- Display Chart in Streamlit ---
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No clients found or error retrieving data.")

clients = get_auditor_dashboard(auditor_id)

if "error" in clients:
    st.error(clients["error"])
else:
    st.subheader("Client Audit Status")
    
    selected_client = st.selectbox("Select a Client to View Evidence", [c["client_id"] for c in clients])
    
    if selected_client:
        st.subheader(f"Submitted Evidence for Client {selected_client}")
        
        evidence_list = get_client_evidence(selected_client)
        # st.write("Debug: API Response for get_client_evidence", evidence_list)

        if not evidence_list or "error" in evidence_list:
            st.error(f"Failed to retrieve evidence: {evidence_list.get('error', 'Invalid server response')}")
        else:
            # Use custom CSS classes for the headings and list items.
            st.markdown('<div class="evidence-section-title">Required Evidence</div>', unsafe_allow_html=True)
            required_evidence = evidence_list.get("evidence_required", [])
            if not required_evidence:
                st.warning("No required evidence listed for this client.")
            else:
                for doc in required_evidence:
                    st.markdown(f'<div class="evidence-list-item">🔵 {doc}</div>', unsafe_allow_html=True)

            st.markdown('<div class="evidence-section-title">Submitted Evidence</div>', unsafe_allow_html=True)
            submitted_evidence = evidence_list.get("evidence_submitted", [])
            if not submitted_evidence:
                st.warning("No evidence submitted yet.")
            else:
                for evidence in submitted_evidence:
                    document_name = evidence.get("document_name")
                    filename = evidence.get("filename")
                    status = evidence.get("status")
                    
                    if not all([document_name, filename, status]):
                        st.error(f"Invalid evidence format: {evidence}")
                        continue

                    st.markdown(
                        f'<div class="evidence-list-item">✅ {document_name} - {filename} ({status})</div>',
                        unsafe_allow_html=True
                    )

st.subheader("Create New Audit Request")
with st.form(key="audit_request_form"):
    client_id = st.text_input("Client ID", help="Enter the Client ID for the audit request")
    email = st.text_input("Client Email", help="Enter the client's email")
    phone = st.text_input("Client Phone", help="Enter the client's phone number")
    deadline = st.date_input("Audit Deadline")

    all_documents = [
        "Balance Sheets", "Income Statements", "Cash Flow Statements",
        "Bank Statements", "Invoices and Bills", "Tax Returns",
        "Tax Registration Certificate", "Share Certificates"
    ]
    selected_documents = st.multiselect("Select Required Evidence Documents", all_documents)

    submit_button = st.form_submit_button("Create Request")

if submit_button:
    if not client_id or not email or not phone or not selected_documents:
        st.error("All fields are required!")
    else:
        request_data = {
            "id": client_id,
            "email": email,
            "phone": phone,
            "deadline": str(deadline),
            "evidence_required": selected_documents
        }
        response = create_audit_request(request_data)

        if "error" in response:
            st.error(response["error"])
        else:
            st.success(f"Audit request created for Client {client_id}!")
            st.success(f"Email sent successfully")
            
            
if st.button("Logout"):
    st.session_state.clear()
    st.success("Logged out successfully! Redirecting to login page...")
    st.rerun()
