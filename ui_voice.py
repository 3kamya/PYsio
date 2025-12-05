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
# Helper: Normalize parser output
# ----------------------------
def normalize_parsed(parsed_list):
    """
    Convert parser list output into a dict keyed by type.
    Ensures consistent storage.
    """
    result = {
        "rom": [],
        "strength": [],
        "swelling": None,
        "pain_level": None,
        "infection_signs": [],
        "mobility_status": []
    }
    for item in parsed_list:
        t = item.get("type")
        if t == "rom":
            result["rom"].append(item)
        elif t == "strength":
            result["strength"].append(item)
        elif t == "swelling":
            result["swelling"] = item.get("present")
        elif t == "pain_level":
            if item.get("pain_level") is not None:
                result["pain_level"] = item.get("pain_level")
        elif t == "infection_signs":
            result["infection_signs"].extend(item.get("signs", []))
        elif t == "mobility_status":
            result["mobility_status"].append(item.get("status"))
    return result

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

    if not any(parsed.values()):
        st.info("No actionable data parsed from transcript.")
        return

    st.subheader("Parsed Values (suggested)")
    st.json(parsed)

    # ----------------------------
    # LOAD EXISTING PATIENT DATA
    # ----------------------------
    patient = get_patient(pid)
    rom_entries = []
    strength_entries = []
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

    # ----------------------------
    # BUILD UPDATES DICT
    # ----------------------------
    updates = {}

    # ROM
    for r in parsed["rom"]:
        rom_entries.append({
            "joint": r["rom_type"],
            "start": r["start"],
            "end": r["end"]
        })
    if rom_entries:
        updates["rom_entries"] = json.dumps(rom_entries)

    # Strength
    for s in parsed["strength"]:
        strength_entries.append({
            "muscle_group": s.get("muscle_group"),
            "grade": s.get("grade")
        })
    if strength_entries:
        updates["strength_entries"] = json.dumps(strength_entries)

    # Swelling
    if parsed["swelling"] is not None:
        updates["swelling"] = "Yes" if parsed["swelling"] else "No"

    # Pain level
    if parsed["pain_level"] is not None:
        updates["pain_level"] = parsed["pain_level"]

    # Infection signs
    if parsed["infection_signs"]:
        updates["infection_signs"] = json.dumps(parsed["infection_signs"])

    # Mobility status
    if parsed["mobility_status"]:
        updates["mobility_status"] = json.dumps(parsed["mobility_status"])

    st.markdown("**Suggested updates:**")
    st.write(updates)

    # ----------------------------
    # APPLY BUTTON
    # ----------------------------
    if st.button("Apply suggested updates to patient"):
        ok = update_patient_fields(pid, updates)
        if ok:
            add_session(pid, transcript, parsed, parsed["pain_level"])
            st.success("Patient record updated and session saved.")
        else:
            st.error("Failed to update patient.")
