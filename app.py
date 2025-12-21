import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

st.set_page_config(page_title="CRM Dashboard", layout="wide")

# LOAD CONFIG
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# AUTH SETUP
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# LOGIN FORM
authenticator.login('main')

# FETCH LOGIN STATE
auth_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")

# WHEN NOT LOGGED IN
if auth_status is None:
    st.warning("⚠️ Please enter username and password")
    st.stop()

# WHEN LOGIN FAILED
elif auth_status is False:
    st.error("❌ Incorrect username or password")
    st.stop()

# WHEN LOGIN SUCCESS
elif auth_status is True:
    # ----------------------------
# SIDEBAR STYLE
# ----------------------------
    st.markdown("""
    <style>

    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #08142c, #0a182f, #0d1e3b);
        color: white;
        padding: 20px;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
        font-size: 15px;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 20px;
    }

    .sidebar-label {
        font-size: 16px;
        font-weight: 600;
        color: #9db7d6 !important;
        margin-top: 18px;
        margin-bottom: 5px;
    }

    div[data-baseweb="select"] > div {
        background-color: #132240 !important;
        border-radius: 10px !important;
        border: 1px solid #3c4f70 !important;
        color: white !important;
    }

    span[data-baseweb="tag"] {
        background-color: #5e82ff !important;
        color: white !important;
        font-weight: 600;
    }

    </style>
    """, unsafe_allow_html=True)
    st.sidebar.success(f"Welcome {name} 👋")
    authenticator.logout("Logout", "sidebar")

    st.markdown("# 📊 CRM Analytics Dashboard")
    st.write("### Welcome to CRM Streamlit App 🚀")
    st.success("✔ Use the left sidebar to open dashboards")
