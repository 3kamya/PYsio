import streamlit as st
from data_model import PatientRecord, ROMEntry, StrengthEntry

def patient_form():
    st.header("Patient Intake Form")

    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.text_input("Sex")
    surgery_date = st.date_input("Surgery Date")
    contact = st.text_input("Contact Number")
    surgical_procedure = st.text_input("Surgical Procedure")

    st.subheader("Post-Operative Status")
    pain_level = st.slider("Pain Level (0-10 VAS)", 0, 10, 0)
    swelling = st.selectbox("Swelling", ["Yes", "No"])
    swelling_location = st.text_input("Swelling Location")
    wound_condition = st.text_area("Wound / Incision Condition")
    infection_signs = st.text_input("Signs of Infection")

    st.subheader("Functional Assessment")
    mobility_status = st.selectbox("Mobility Status", 
                                   ["Walking unaided", "With aid", "Wheelchair", "Bedridden"])
    transfer_status = st.selectbox("Bed-to-chair transfers", ["Independent", "Assistance required"])
    bathing = st.selectbox("Bathing", ["Independent", "Assistance"])
    dressing = st.selectbox("Dressing", ["Independent", "Assistance"])
    toileting = st.selectbox("Toileting", ["Independent", "Assistance"])

    st.subheader("Range of Motion (ROM)")
    rom_entries = []
    rom_count = st.number_input("How many joints to enter?", 0, 10, 0)
    for i in range(rom_count):
        st.write(f"### Joint {i+1}")
        joint = st.text_input(f"Joint {i+1}")
        active = st.text_input(f"Active ROM {i+1}")
        passive = st.text_input(f"Passive ROM {i+1}")
        rom_entries.append(ROMEntry(joint, active, passive))

    st.subheader("Muscle Strength (0–5)")
    strength_entries = []
    strength_count = st.number_input("How many muscle groups?", 0, 10, 0)
    for i in range(strength_count):
        st.write(f"### Muscle Group {i+1}")
        mg = st.text_input(f"Muscle Group {i+1}")
        grade = st.text_input(f"Strength Grade {i+1}")
        strength_entries.append(StrengthEntry(mg, grade))

    pain_behavior = st.text_area("Pain Behavior & Triggers")
    balance_gait = st.text_area("Balance & Gait")

    st.subheader("Home Care Treatment Plan")
    ice = st.text_input("Ice Application Instructions")
    elevation = st.text_input("Elevation Guidelines")
    compression = st.text_input("Compression Use")

    rom_exercises = st.text_area("ROM Exercises")
    strength_exercises = st.text_area("Strengthening Exercises")
    mobility_training = st.text_area("Functional Mobility Training")

    home_modifications = st.text_area("Home Environment Modifications")
    assistive_devices = st.text_input("Assistive Devices")

    wound_care = st.text_area("Wound Care Instructions")
    report_signs = st.text_area("Signs to Report")
    medications = st.text_area("Medication & Pain Management")

    st.subheader("Progress Monitoring")
    assessment_date = st.date_input("Assessment Date")
    follow_pain = st.slider("Follow-up Pain Level", 0, 10, 0)
    follow_swelling = st.selectbox("Swelling (follow-up)", ["Yes", "No"])
    rom_improve = st.text_area("ROM Improvements")
    strength_changes = st.text_area("Strength Changes")
    functional_gains = st.text_area("Functional Gains")
    next_visit = st.date_input("Next Visit / Call")
    notes = st.text_area("Additional Notes")

    if st.button("Save Patient Record"):
        return PatientRecord(
            name, age, sex, str(surgery_date), contact, surgical_procedure,
            str(pain_level), swelling, swelling_location, wound_condition, infection_signs,
            mobility_status, transfer_status, bathing, dressing, toileting,
            rom_entries, strength_entries,
            pain_behavior, balance_gait,
            ice, elevation, compression,
            rom_exercises, strength_exercises, mobility_training,
            home_modifications, assistive_devices,
            wound_care, report_signs, medications,
            str(assessment_date), str(follow_pain), follow_swelling,
            rom_improve, strength_changes, functional_gains,
            str(next_visit), notes
        )
    return None
