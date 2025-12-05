import streamlit as st
from datetime import datetime
from ui_module import patient_form
from analytics import analytics_dashboard
from ui_voice import voice_note_ui
from compat_shim import (
    save_record_sql,
    load_all_patients_sql,
    load_single_patient_sql,
    generate_patient_pdf,
    convert_voice_to_text,
    extract_structured_keywords
)


# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(
    page_title="PYsio — Physiotherapy Tracker",
    page_icon="💪",
    layout="wide"
)


# ----------------------------------------------------
# SIMPLE LOGIN SYSTEM (LOCAL AUTH)
# ----------------------------------------------------
def login_system():
    st.sidebar.title("Login")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        if username == "physio" and password == "1234":
            st.session_state["logged_in"] = True
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

    if "logged_in" not in st.session_state:
        st.stop()


login_system()


# ----------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", [
    "Home",
    "Add Patient",
    "View Patients",
    "Voice Notes",
    "Analytics Dashboard",
    "Export PDF",
    "Settings"
])


# ----------------------------------------------------
# HOME PAGE
# ----------------------------------------------------
if page == "Home":
    st.title("PYsio — Physiotherapy Patient Tracker")
    st.markdown("""
    A complete physiotherapy assistant for tracking:
    - Post-operative patient assessment  
    - ROM & Strength  
    - Home exercise programs  
    - Progress monitoring  
    - Voice-to-data automation  
    """)

    st.image("https://cdn-icons-png.flaticon.com/512/14069/14069128.png", width=200)


# ----------------------------------------------------
# ADD PATIENT PAGE
# ----------------------------------------------------
elif page == "Add Patient":
    st.title("Add New Patient Record")

    record = patient_form()
    if record:
        save_record_sql(record)
        st.success("Patient record saved successfully!")


# ----------------------------------------------------
# VIEW PATIENTS PAGE
# ----------------------------------------------------
elif page == "View Patients":
    st.title("All Patients")

    df = load_all_patients_sql()
    st.dataframe(df)

    st.subheader("View Specific Patient")

    if not df.empty:
        patient_ids = df["patient_id"].tolist()
        picked_id = st.selectbox("Select Patient ID", patient_ids)

        if st.button("Load Patient"):
            patient_data = load_single_patient_sql(picked_id)
            st.write(patient_data)


# ----------------------------------------------------
# VOICE NOTES PAGE
# ----------------------------------------------------
elif page == "Voice Notes":
    st.title("Voice-to-Data Assistant")

    st.info("Record your session summary. The system extracts keywords such as ROM, pain, strength.")

    audio_file = voice_note_ui()

    if audio_file:
        text = convert_voice_to_text(audio_file)
        st.subheader("Transcribed Text")
        st.write(text)

        structured_data = extract_structured_keywords(text)
        st.subheader("Extracted Data")
        st.json(structured_data)

        st.success("This data can now auto-populate patient fields (Week 6).")


# ----------------------------------------------------
# ANALYTICS PAGE (WEEK 5)
# ----------------------------------------------------
elif page == "Analytics Dashboard":
    analytics_dashboard()


# ----------------------------------------------------
# PDF EXPORT PAGE
# ----------------------------------------------------
elif page == "Export PDF":
    st.title("Export Patient Record as PDF")

    patients = load_all_patients_sql()

    if not patients.empty:
        patient_id = st.selectbox("Select Patient ID", patients["patient_id"].tolist())

        if st.button("Generate PDF"):
            pdf_path = generate_patient_pdf(patient_id)
            st.success("PDF generated successfully!")
            st.download_button("Download PDF", open(pdf_path, "rb"), file_name="patient_record.pdf")


# ----------------------------------------------------
# SETTINGS PAGE
# ----------------------------------------------------
elif page == "Settings":
    st.title("App Settings")

    st.write("Current Database: PostgreSQL")
    st.write("More settings coming soon…")


# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------
st.markdown("---")
st.caption("Developed with ❤️ for physiotherapists, and my dear sister — PYsio 2025")
