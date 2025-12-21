import streamlit as st
import yaml
from yaml.loader import SafeLoader

import streamlit_authenticator as stauth


st.set_page_config(page_title="CRM Dashboard", layout="wide")


# -------------------------
# LOAD YAML CONFIG
# -------------------------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


# -------------------------
# AUTHENTICATION
# -------------------------
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

name, auth_status, username = authenticator.login(
    form_name='Login',
    location='main'
)



# -------------------------
# CHECK LOGIN STATUS
# -------------------------
if auth_status:

    # SUCCESS LOGIN
    st.sidebar.success(f"Welcome: {name}")
    authenticator.logout("Logout", "sidebar")

    # -------------------------
    # DASHBOARD CONTENT BELOW
    # -------------------------

    st.markdown("# 📊 CRM Analytics Dashboard")
    st.write("### Welcome to CRM Streamlit App 🚀")
    st.success("✔ Use the left sidebar to open dashboards")

elif auth_status == False:
    st.error("❌ Incorrect username or password")

elif auth_status == None:
    st.warning("⚠️ Please enter username and password")
    st.stop()