import streamlit as st
from ui_module import patient_form
from data_module import save_record, load_records
from datetime import datetime


st.set_page_config(
    page_title="PYsio — Physiotherapy Tracker",
    page_icon="💪",
    layout="wide"
)

# ------------------------------
# HEADER
# ------------------------------
st.title("💪 PYsio: Physiotherapy Patient Tracker")
st.markdown("Welcome! Manage patients, record progress, and keep notes all in one place.")

# Sidebar Navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", [
    "🏠 Home",
    "🧍‍♂️ Patient Records",
    "🗣️ Voice Notes",
    "📈 Progress Reports",
    "⚙️ Settings"
])

# ------------------------------
# HOME PAGE
# ------------------------------
if page == "🏠 Home":
    st.header("Dashboard Overview")
    st.write("This is the central hub of your physiotherapy tracker.")
    st.write("""
        **Features:**
        - Add and view patient records
        - Record voice notes using speech recognition
        - Generate visual progress reports
        - Save everything securely in a local or cloud database
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/14069/14069128.png", width=200)

# ------------------------------
# PATIENT RECORDS PAGE
# ------------------------------
elif page == "🧍‍♂️ Patient Records":
    st.header("📋 Manage Patient Records")
    st.subheader("Add New Patient")

    with st.form("add_patient_form"):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", 0, 120, 30)
        condition = st.text_area("Condition / Diagnosis")
        start_date = st.date_input("Start Date", datetime.now())
        submit = st.form_submit_button("Add Patient")

        if submit:
            # (Later, save to database here)
            st.success(f"Patient '{name}' added successfully!")

    st.markdown("---")
    st.subheader("View Existing Patients")
    st.info("This will display data fetched from your database once connected.")

# ------------------------------
# VOICE NOTES PAGE
# ------------------------------
elif page == "🗣️ Voice Notes":
    st.header("🎙️ Record Voice Notes")

    st.write("Record quick notes for a patient session using voice-to-text.")
    if st.button("Start Recording"):
        st.warning("Recording feature coming soon! (will integrate with `voice_module.py`)")

# ------------------------------
# PROGRESS REPORTS PAGE
# ------------------------------
elif page == "📈 Progress Reports":
    st.header("📊 Patient Progress Reports")
    st.write("This section will visualize patient progress using charts and analytics.")
    st.info("You’ll connect this later using Matplotlib or Plotly.")

# ------------------------------
# SETTINGS PAGE
# ------------------------------
elif page == "⚙️ Settings":
    st.header("⚙️ App Settings")
    st.write("Choose your data storage option (Cloudflare, Firebase, or Local Database).")
    st.radio("Database:", ["Local (SQLite)", "Firebase", "PostgreSQL"])
    st.button("Save Settings")

# ------------------------------
# FOOTER
# ------------------------------
st.markdown("---")
st.caption("Developed with ❤️ for physiotherapists, and my dear sister | PYsio 2025")
def main():
    st.title("Physiotherapy Post-Op Assistant")

    menu = st.sidebar.selectbox("Menu", ["New Patient Entry", "View Saved Records"])

    if menu == "New Patient Entry":
        record = patient_form()
        if record:
            save_record(record)
            st.success("Patient record saved successfully!")

    elif menu == "View Saved Records":
        records = load_records()
        st.write("### Saved Records")
        st.dataframe(records)

if __name__ == "__main__":
    main()
