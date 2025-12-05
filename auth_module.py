# auth_ui.py
import streamlit as st
from datamod_sql import verify_user, add_user

def auth_ui():
    st.sidebar.subheader("Account")
    menu = st.sidebar.selectbox("Choose", ["Login", "Sign up"])
    if menu == "Sign up":
        st.sidebar.text_input("Username", key="su_username")
        st.sidebar.text_input("Password", key="su_password", type="password")
        if st.sidebar.button("Create account"):
            ok = add_user(st.session_state.su_username, st.session_state.su_password)
            if ok:
                st.sidebar.success("Account created. Please log in.")
            else:
                st.sidebar.error("Failed to create account (maybe already exists).")
        st.stop()
    else:
        st.sidebar.text_input("Username", key="login_username")
        st.sidebar.text_input("Password", key="login_password", type="password")
        if st.sidebar.button("Login"):
            if verify_user(st.session_state.login_username, st.session_state.login_password):
                st.session_state.logged_in = True
                st.session_state.user = st.session_state.login_username
                st.sidebar.success("Logged in")
            else:
                st.sidebar.error("Invalid credentials")
        if st.session_state.get("logged_in"):
            st.sidebar.write(f"Logged in as: {st.session_state.user}")
