# auth.py
import streamlit as st

def initialize_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "history" not in st.session_state:
        st.session_state.history = []


def login_page():
    st.title("🔐 Bridge17 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Select Sector", ["NGO", "PSUs", "Government"])

    if st.button("Login"):
        if username and password:
            st.session_state.authenticated = True
            st.session_state.user_role = role
            st.success(f"Welcome {username} ({role})")
            st.rerun()
        else:
            st.error("Please enter credentials")
