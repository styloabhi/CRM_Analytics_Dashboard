import streamlit as st
# 🔐 Page security check
if st.session_state["authentication_status"] != True:
    st.error("Please login first.")
    st.stop()
