import streamlit as st

VALID_USERS = {
    "physio1": "password123",
    "physio2": "1234"
}

def login():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in VALID_USERS and VALID_USERS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.success("Login successful")
        else:
            st.error("Invalid username or password")

    return st.session_state.get("logged_in", False)
