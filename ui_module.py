import streamlit as st
import uuid

def patient_form():
    st.header("Patient Intake Form")

    # ---------------- PATIENT INFO -----------------
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    sex = st.text_input("Sex")
    surgery_date = st.date_input("Surgery Date")
    contact = st.text_input("Contact Number")
    surgical_procedure = st.text_input("Surgical Procedure")

    st.subheader("Post-Operative Status")
    pain_level = st.slider("Pain Level (0-10 VAS)", 0, 10, 0)
    swelling = st.selectbox("Swelling", ["Yes", "No"])
    swelling = True if swelling == "Yes" else False
    swelling_location = st.text_input("Swelling Location")
    wound_condition = st.text_area("Wound / Incision Condition")
    infection_signs = st.text_input("Signs of Infection")

    # ---------------- FUNCTIONAL -----------------
    mobility_status = st.selectbox("Mobility Status", 
        ["Walking unaided", "With aid", "Wheelchair", "Bedridden"])
    transfer_status = st.selectbox("Bed-to-chair transfers", 
        ["Independent", "Assistance required"])
    bathing = st.selectbox("Bathing", ["Independent", "Assistance"])
    dressing = st.selectbox("Dressing", ["Independent", "Assistance"])
    toileting = st.selectbox("Toileting", ["Independent", "Assistance"])

    # ---------------- ROM ENTRIES -----------------
    st.subheader("Range of Motion (ROM)")
    rom_entries = []
    rom_count = st.number_input("How many joints?", 0, 10, 0)

    for i in range(rom_count):
        st.write(f"### Joint {i+1}")
        joint = st.text_input(f"Joint {i+1}")
        active = st.number_input(f"Active ROM {i+1}", step=0.1)
        passive = st.number_input(f"Passive ROM {i+1}", step=0.1)

        rom_entries.append({
            "joint": joint,
            "active": active,
            "passive": passive
        })

    # ---------------- STRENGTH -----------------
    st.subheader("Muscle Strength (0–5)")
    strength_entries = []
    strength_count = st.number_input("How many muscle groups?", 0, 10, 0)

    for i in range(strength_count):
        st.write(f"### Muscle Group {i+1}")
        mg = st.text_input(f"Muscle Group {i+1}")
        grade = st.number_input(f"Strength Grade {i+1}", 0, 5, 0)
        strength_entries.append({
            "muscle_group": mg,
            "grade": grade
        })

    # ---------------- REMAINING FIELDS -----------------
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
    follow_swelling = True if follow_swelling == "Yes" else False

    rom_improve = st.text_area("ROM Improvements")
    strength_changes = st.text_area("Strength Changes")
    functional_gains = st.text_area("Functional Gains")
    next_visit = st.date_input("Next Visit / Call")
    notes = st.text_area("Additional Notes")

    if st.button("Save Patient Record"):
        patient_id = str(uuid.uuid4())

        return {
            "patient_id": patient_id,
            "name": name,
            "age": age,
            "sex": sex,
            "surgery_date": str(surgery_date),
            "contact": contact,
            "surgical_procedure": surgical_procedure,
            "pain_level": pain_level,
            "swelling": swelling,
            "swelling_location": swelling_location,
            "wound_condition": wound_condition,
            "infection_signs": infection_signs,
            "mobility_status": mobility_status,
            "transfer_status": transfer_status,
            "bathing": bathing,
            "dressing": dressing,
            "toileting": toileting,
            "rom_entries": rom_entries,
            "strength_entries": strength_entries,
            "pain_behavior": pain_behavior,
            "balance_gait": balance_gait,
            "ice": ice,
            "elevation": elevation,
            "compression": compression,
            "rom_exercises": rom_exercises,
            "strength_exercises": strength_exercises,
            "mobility_training": mobility_training,
            "home_modifications": home_modifications,
            "assistive_devices": assistive_devices,
            "wound_care": wound_care,
            "report_signs": report_signs,
            "medications": medications,
            "assessment_date": str(assessment_date),
            "follow_pain": follow_pain,
            "follow_swelling": follow_swelling,
            "rom_improve": rom_improve,
            "strength_changes": strength_changes,
            "functional_gains": functional_gains,
            "next_visit": str(next_visit),
            "notes": notes
        }

    return None
