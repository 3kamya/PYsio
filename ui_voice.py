# ui_voice.py
import streamlit as st
import json
from voice_module import transcribe_uploaded_file, transcribe_microphone
from voice_parser import extract_rom_data
from datamod_sql import (
    get_all_patients, find_patient_by_name, add_session,
    update_patient_fields, get_patient, get_sessions_for_patient
)

# ----------------------------
# FIX: Normalize parsed output
# ----------------------------
def normalize_parsed(parsed):
    """
    Ensures parsed is ALWAYS a dictionary.
    If parsed is a list, return the first dictionary.
    If parsed is None or empty, return {}.
    """
    if parsed is None:
        return {}

    if isinstance(parsed, list):
        if len(parsed) > 0 and isinstance(parsed[0], dict):
            return parsed[0]
        else:
            return {}

    if isinstance(parsed, dict):
        return parsed

    return {}  # fallback


# ----------------------------
# MAIN UI FUNCTION
# ----------------------------
def voice_note_ui():
    st.header("Voice Notes — Transcribe & Auto-Fill")

    patients = get_all_patients()
    if not patients:
        st.warning("No patients found. Add a patient first in Patient Records.")
        return

    # patient selector
    options = [f"{p['id']} — {p['name']}" for p in patients]
    selected = st.selectbox("Select patient to update", options)
    pid = int(selected.split(" — ")[0])

    st.write("Upload audio, record, or paste transcript:")
    uploaded = st.file_uploader("Upload audio (wav/mp3)", type=["wav", "mp3", "m4a"])
    manual_text = st.text_area("Or paste transcript here")

    parsed = None
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

    # STOP if nothing parsed
    if parsed is None:
        return

    # --------------------------------
    # FIX: ALWAYS ENSURE parsed IS A DICT
    # --------------------------------
    parsed = normalize_parsed(parsed)

    st.subheader("Parsed Values (suggested)")
    st.json(parsed)

    # --------------------------------
    # BUILD PATIENT UPDATE FIELDS
    # --------------------------------
    updates = {}

    # Pain
    if parsed.get("pain_level") is not None:
        updates["pain_level"] = parsed["pain_level"]

    # Swelling
    if parsed.get("swelling") is not None:
        swelling_data = parsed["swelling"]
        if isinstance(swelling_data, dict):
            updates["swelling"] = "Yes" if swelling_data.get("present") else "No"
            if swelling_data.get("location"):
                updates["swelling_location"] = swelling_data["location"]

    # ROM
    # --- ROM ---
if parsed.get("rom"):
    patient = get_patient(pid)

    # Load existing latest ROM (for quick view)
    rom_entries = []
    if patient and patient.get("rom_entries"):
        try:
            rom_entries = json.loads(patient["rom_entries"])
        except:
            rom_entries = []

    # Save each parsed ROM entry
    for item in parsed["rom"]:
        rom_type = item["rom_type"]
        start_val = item["start"]
        end_val = item["end"]

        # 1. Save in patient.latest ROM
        rom_entries.append({
            "joint": rom_type,
            "start": start_val,
            "end": end_val
        })

        # 2. Save to rom_progress table
        add_rom_progress(pid, rom_type, start_val, end_val)

    updates["rom_entries"] = json.dumps(rom_entries)

    # Strength
    if parsed.get("strength"):
        patient = get_patient(pid)
        strength_entries = []
        if patient and patient.get("strength_entries"):
            try:
                strength_entries = json.loads(patient["strength_entries"])
            except:
                strength_entries = []

        for s in parsed["strength"]:
            strength_entries.append({"muscle_group": s[0], "grade": s[1]})

        updates["strength_entries"] = strength_entries

    st.markdown("**Suggested updates:**")
    st.write(updates)

    # --------------------------------
    # APPLY BUTTON
    # --------------------------------
    if st.button("Apply suggested updates to patient"):
        ok = update_patient_fields(pid, updates)
        if ok:
            add_session(pid, transcript, parsed, parsed.get("pain_level"))
            st.success("Patient record updated and session saved.")
        else:
            st.error("Failed to update patient.")
