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

from api import login, register_client

if "show_register" not in st.session_state:
    st.session_state.show_register = False

st.title("Autonomous Audit AI Evidence Collection")
st.subheader("Login")

role = st.selectbox("Select Role", ["Client", "Auditor"])
client_id = st.text_input("Enter your unique ID", key="login_client_id")
password = st.text_input("Enter Password", type="password", key="login_password")

# Login Button
if st.button("Login"):
    if not client_id.strip() or not password.strip():
        st.error("Client ID and password are required.")
    else:
        response = login(client_id, password, role.lower())

        if "error" in response:
            st.error(response["error"])
        else:
            st.success("Login successful!")

            # Store session details
            st.session_state["role"] = role.lower()
            st.session_state["user_id"] = client_id

            # Redirect user based on role
            if role.lower() == "client":
                st.switch_page("pages/client_dashboard.py")
            else:
                st.switch_page("pages/auditor_dashboard.py")

# Divider
st.markdown("---")

if st.button("New Client? Register Here"):
    st.session_state.show_register = not st.session_state.show_register
    st.rerun()  # Refresh the page to apply changes

if st.session_state.show_register:
    st.subheader("Client Registration")

    client_id_reg = st.text_input("Client ID", key="register_client_id")
    company_name = st.text_input("Company Name", key="register_company_name")
    phone = st.text_input("Phone Number", key="register_phone")
    email = st.text_input("Email", key="register_email")
    address = st.text_area("Address", key="register_address")
    password_reg = st.text_input("Password", type="password", key="register_password")
    retype_password = st.text_input("Retype Password", type="password", key="register_retype_password")

    if st.button("Register"):
        if not client_id_reg or not company_name or not phone or not email or not address or not password_reg or not retype_password:
            st.error("All fields are required for registration.")
        elif password_reg != retype_password:
            st.error("Passwords do not match.")
        else:
            response = register_client(client_id_reg, company_name, phone, email, address, password_reg, retype_password)
            if "error" in response:
                st.error(response["error"])
            else:
                st.success("Registration successful! Please log in.")
                st.session_state.show_register = False
                st.rerun()
