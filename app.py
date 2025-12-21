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
    st.sidebar.success(f"Welcome {name} 👋")
    authenticator.logout("Logout", "sidebar")

    st.markdown("# 📊 CRM Analytics Dashboard")
    st.write("### Welcome to CRM Streamlit App 🚀")
    st.success("✔ Use the left sidebar to open dashboards")
