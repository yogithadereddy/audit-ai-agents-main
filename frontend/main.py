import streamlit as st
import os

# Set page configuration first — very important!
st.set_page_config(page_title="Audit AI Agent", page_icon="📑", layout="wide")

# Get absolute path to styles.css
current_dir = os.path.dirname(__file__)
css_path = os.path.join(current_dir, "styles.css")

# Read and inject CSS
with open(css_path) as f:
    css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("/Users/kdnai_dyogitha/Documents/PROJECTS/PROJECT-1/audit-ai-agents-main/frontend/static/logo.png", width=130)
st.sidebar.title("Navigation")

# Session-based navigation
if "user_id" in st.session_state:
    role = st.session_state.get("role")

    if role == "client":
        st.sidebar.page_link("pages/client_dashboard.py", label="Client Dashboard")
    elif role == "auditor":
        st.sidebar.page_link("pages/auditor_dashboard.py", label="Auditor Dashboard")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.switch_page("pages/login.py")
else:
    st.write("Please log in to access the dashboard.")
    st.page_link("pages/login.py", label="Go to Login", icon="🔐")
