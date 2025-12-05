# ui_voice.py
import streamlit as st
import json
from voice_module import transcribe_uploaded_file, transcribe_microphone
from voice_parser import extract_rom_data
from datamod_sql import (
    get_all_patients, get_patient, add_session,
    update_patient_fields
)

# ----------------------------
# FIX: Normalize parsed output
# ----------------------------
def normalize_parsed(parsed):
    """
    Ensure parsed is always a list of dicts.
    """
    if parsed is None:
        return []
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [p for p in parsed if isinstance(p, dict)]
    return []

# ----------------------------
# MAIN UI FUNCTION
# ----------------------------
def voice_note_ui():
    st.header("Voice Notes — Transcribe & Auto-Fill")

    patients = get_all_patients()
    if not patients:
        st.warning("No patients found. Add a patient first in Patient Records.")
        return

    # Patient selector
    options = [f"{p['id']} — {p['name']}" for p in patients]
    selected = st.selectbox("Select patient to update", options)
    pid = int(selected.split(" — ")[0])

    st.write("Upload audio, record, or paste transcript:")
    uploaded = st.file_uploader("Upload audio (wav/mp3)", type=["wav", "mp3", "m4a"])
    manual_text = st.text_area("Or paste transcript here")

    parsed = []
    transcript = ""

    col1, col2 = st.columns(2)

    # ----------------------------
    # MICROPHONE
    # ----------------------------
    with col1:
        if st.button("Record from Microphone (short)"):
            st.info("Recording... speak now")
            transcript = transcribe_microphone()
            st.subheader("Transcript")
            st.write(transcript)
            parsed = extract_rom_data(transcript)

    # ----------------------------
    # UPLOAD OR PASTED TEXT
    # ----------------------------
    with col2:
        if st.button("Transcribe Upload / Paste"):
            if uploaded:
                transcript = transcribe_uploaded_file(uploaded)
            elif manual_text:
                transcript = manual_text
            else:
                st.error("Please upload audio or paste text.")
                return

            st.subheader("Transcript")
            st.write(transcript)
            parsed = extract_rom_data(transcript)

    parsed = normalize_parsed(parsed)

    if not parsed:
        st.info("No actionable data parsed from transcript.")
        return

    st.subheader("Parsed Values (suggested)")
    st.json(parsed)

    # ----------------------------
    # BUILD PATIENT UPDATE FIELDS
    # ----------------------------
    updates = {}
    rom_entries = []
    strength_entries = []
    swelling = None
    pain_level = None
    infection_signs = []
    mobility_status = []

    # Load existing patient data
    patient = get_patient(pid)
    if patient:
        if patient.get("rom_entries"):
            try:
                rom_entries = json.loads(patient["rom_entries"])
            except:
                rom_entries = []
        if patient.get("strength_entries"):
            try:
                strength_entries = json.loads(patient["strength_entries"])
            except:
                strength_entries = []

    # Parse each entry from the parser
    for item in parsed:
        if item.get("type") == "rom":
            rom_entries.append({
                "joint": item.get("rom_type"),
                "start": item.get("start"),
                "end": item.get("end")
            })
        elif item.get("type") == "strength":
            strength_entries.append({
                "muscle_group": item.get("muscle_group"),
                "grade": item.get("grade")
            })
        elif item.get("type") == "swelling":
            swelling = item.get("present")
        elif item.get("type") == "pain_level":
            pain_level = item.get("pain_level")
        elif item.get("type") == "infection_signs":
            infection_signs.extend(item.get("signs", []))
        elif item.get("type") == "mobility_status":
            mobility_status.append(item.get("status"))

    # Build updates dict
    if rom_entries:
        updates["rom_entries"] = json.dumps(rom_entries)
    if strength_entries:
        updates["strength_entries"] = json.dumps(strength_entries)
    if swelling is not None:
        updates["swelling"] = "Yes" if swelling else "No"
    if pain_level is not None:
        updates["pain_level"] = pain_level
    if infection_signs:
        updates["infection_signs"] = json.dumps(infection_signs)
    if mobility_status:
        updates["mobility_status"] = json.dumps(mobility_status)

    st.markdown("**Suggested updates:**")
    st.write(updates)

    # ----------------------------
    # APPLY BUTTON
    # ----------------------------
    if st.button("Apply suggested updates to patient"):
        ok = update_patient_fields(pid, updates)
        if ok:
            add_session(pid, transcript, parsed, pain_level)
            st.success("Patient record updated and session saved.")
        else:
            st.error("Failed to update patient.")
