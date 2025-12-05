
import streamlit as st
import pandas as pd
from datetime import datetime
from ui_module import patient_form

# --- UPDATED IMPORTS: ONLY importing the two remaining functions ---
from data_visualisation import (
    plot_strength_progress, 
    plot_pain_trend
)
# ------------------------------------------------------------------

from ui_voice import voice_note_ui
from compat_shim import (
    save_record_sql,
    load_all_patients_sql,
    load_single_patient_sql,
    generate_patient_pdf,
    convert_voice_to_text,
    extract_structured_keywords,
    add_session,
    get_sessions_for_patient # Ensure this is here for the View Patients section
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
page = st.sidebar.radio("Go to:", [
    "Home",
    "Add / Update Patient Session",    # <-- changed
    "View Patients",
    "Voice Notes",
    "Visualisation Dashboard",
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
            # Use get_sessions_for_patient function
            sessions = get_sessions_for_patient(int(picked_id)) 
            
            st.subheader(f"Patient Record: ID {picked_id}")
            st.json(patient_data)
            
            st.subheader("Session History")
            
            if sessions:
                # Convert the sessions list of dicts to a DataFrame for clean display
                sessions_df = pd.DataFrame(sessions)
                
                # Format the DataFrame to make it readable (optional but recommended)
                # Drop long JSON fields for cleaner table view
                sessions_df = sessions_df.drop(columns=['parsed_data'], errors='ignore')
                sessions_df['timestamp'] = pd.to_datetime(sessions_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                sessions_df = sessions_df.rename(columns={'timestamp': 'Date/Time'})
                
                st.dataframe(sessions_df)
                
            else:
                st.info("No session history found for this patient.")

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
# VISUALISATION DASHBOARD
# ----------------------------------------------------
elif page == "Visualisation Dashboard":
    st.title("📊 Patient Data Visualisation")

    df = load_all_patients_sql()

    if df.empty:
        st.warning("No patients found.")
    else:
        selected_id = st.selectbox("Select Patient", df["patient_id"].tolist())

        if st.button("Generate Visualisations"):
            st.info("Generating visualisation charts for Pain and Strength...")

            # --- ONLY calling the two existing functions ---
            p1 = plot_strength_progress(selected_id)
            p2 = plot_pain_trend(selected_id)

            st.success("Charts generated!")

            # --- ONLY including the two existing paths ---
            imgs = [p1, p2] 

            for img in imgs:
                if img:
                    st.image(img, caption=img, use_column_width=True)

# ----------------------------------------------------
# ADD / UPDATE PATIENT SESSION PAGE
# ----------------------------------------------------
elif page == "Add / Update Patient Session":
    st.title("Add / Update Patient Session")

    # Load existing patients
    df = load_all_patients_sql()
    if df.empty:
        st.warning("No patients found. Please add a new patient first.")
        record = patient_form()
        if record:
            save_record_sql(record)
            st.success("Patient record saved successfully!")
    else:
        patient_ids = df["patient_id"].tolist()
        selected_id = st.selectbox("Select Patient", patient_ids)

        # Option to create a new patient instead
        if st.checkbox("Create a new patient instead"):
            record = patient_form()
            if record:
                save_record_sql(record)
                st.success("New patient record saved!")
        else:
            st.info("Fill out the session details for this patient.")

            # Show the patient form
            session_record = patient_form()
            if session_record:
                # Remove patient_id so we don't overwrite the original patient
                session_record.pop("patient_id", None)

                # Add as a new session
                add_session(
                    int(selected_id),        # patient id
                    transcript="",           # no voice transcript
                    parsed=session_record,   # the manual form data
                    pain_level=session_record.get("pain_level")
                )
                st.success("Session added for existing patient!")



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
