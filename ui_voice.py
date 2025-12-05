import streamlit as st
import json
# Keep your existing imports
from voice_module import transcribe_uploaded_file, transcribe_microphone
from voice_parser import extract_rom_data
from datamod_sql import get_all_patients, get_patient, add_session, update_patient_fields

# Keep your normalize_parsed function exactly as it is
def normalize_parsed(parsed_list):
    # ... (Keep your existing code here) ...
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
# MAIN UI FUNCTION (FIXED)
# ----------------------------
def voice_note_ui():
    st.header("Voice Notes — Transcribe & Auto-Fill")

    # 1. INITIALIZE SESSION STATE
    # We need to remember these values across reruns (between Record and Apply)
    if "v_transcript" not in st.session_state:
        st.session_state["v_transcript"] = ""
    if "v_parsed" not in st.session_state:
        st.session_state["v_parsed"] = {}

    patients = get_all_patients()
    if not patients:
        st.warning("No patients found. Add a patient first in Patient Records.")
        return

    options = [f"{p['id']} — {p['name']}" for p in patients]
    selected = st.selectbox("Select patient to update", options)
    pid = int(selected.split(" — ")[0])

    st.write("Upload audio, record, or paste transcript:")
    uploaded = st.file_uploader("Upload audio (wav/mp3)", type=["wav", "mp3", "m4a"])
    manual_text = st.text_area("Or paste transcript here")

    col1, col2 = st.columns(2)

    # ----------------------------
    # MICROPHONE
    # ----------------------------
    with col1:
        if st.button("Record from Microphone (short)"):
            st.info("Recording... speak now")
            transcript = transcribe_microphone()
            
            # SAVE TO SESSION STATE
            st.session_state["v_transcript"] = transcript
            raw_parsed = extract_rom_data(transcript)
            st.session_state["v_parsed"] = normalize_parsed(raw_parsed)

    # ----------------------------
    # UPLOAD OR PASTED TEXT
    # ----------------------------
    with col2:
        if st.button("Transcribe Upload / Paste"):
            transcript = ""
            if uploaded:
                transcript = transcribe_uploaded_file(uploaded)
            elif manual_text:
                transcript = manual_text
            else:
                st.error("Please upload audio or paste text.")
            
            # SAVE TO SESSION STATE (Only if we got a transcript)
            if transcript:
                st.session_state["v_transcript"] = transcript
                raw_parsed = extract_rom_data(transcript)
                st.session_state["v_parsed"] = normalize_parsed(raw_parsed)

    # ----------------------------
    # DISPLAY CURRENT STATE
    # ----------------------------
    # Always display from session_state, not local variables
    if st.session_state["v_transcript"]:
        st.subheader("Transcript")
        st.write(st.session_state["v_transcript"])

    parsed = st.session_state["v_parsed"]

    # Check actionable data
    def has_actionable_data(parsed_dict):
        if not parsed_dict: return False
        return any([
            parsed_dict.get("pain_level") is not None,
            parsed_dict.get("swelling") is not None,
            parsed_dict.get("rom"),
            parsed_dict.get("strength"),
            parsed_dict.get("infection_signs"),
            parsed_dict.get("mobility_status")
        ])

    if not has_actionable_data(parsed):
        st.info("No actionable data parsed yet.")
        return

    st.subheader("Parsed Values (suggested)")
    st.json(parsed)

    # ----------------------------
    # BUILD UPDATES DICT
    # ----------------------------
    # Rerun the logic to build 'updates' based on the persistent 'parsed' data
    patient = get_patient(pid)
    updates = {}

    # ROM Logic
    rom_entries_existing = []
    if patient.get("rom_entries"):
        try:
            rom_entries_existing = json.loads(patient["rom_entries"])
        except:
            rom_entries_existing = []

    if "rom" in parsed:
        for r in parsed["rom"]:
            joint = r.get("rom_type") or r.get("joint")
            if joint:
                rom_entries_existing.append({
                    "joint": joint,
                    "start": r.get("start"),
                    "end": r.get("end")
                })
        if parsed["rom"]: # Only update if new ROM data exists
            updates["rom_entries"] = json.dumps(rom_entries_existing)

    # Strength Logic
    strength_entries_existing = []
    if patient.get("strength_entries"):
        try:
            strength_entries_existing = json.loads(patient["strength_entries"])
        except:
            strength_entries_existing = []

    if "strength" in parsed:
        for s in parsed["strength"]:
            mg = s.get("muscle_group") or s.get("muscle")
            grade = s.get("grade")
            if mg is not None and grade is not None:
                strength_entries_existing.append({
                    "muscle_group": mg,
                    "grade": grade
                })
        if parsed["strength"]:
            updates["strength_entries"] = json.dumps(strength_entries_existing)

    # Simple Fields
    if parsed.get("swelling") is not None:
        updates["swelling"] = "Yes" if parsed["swelling"] else "No"

    if parsed.get("pain_level") is not None:
        updates["pain_level"] = parsed["pain_level"]

    if parsed.get("infection_signs"):
        updates["infection_signs"] = json.dumps(parsed["infection_signs"])

    if parsed.get("mobility_status"):
        updates["mobility_status"] = json.dumps(parsed["mobility_status"])

    st.markdown("**Suggested updates:**")
    st.write(updates)

    # ----------------------------
    # APPLY BUTTON
    # ----------------------------
    if st.button("Apply suggested updates to patient"):
        if updates:
            # We use the transcript from session_state for the session log
            transcript_to_save = st.session_state["v_transcript"]
            
            ok = update_patient_fields(pid, updates)
            add_session(pid, transcript_to_save, parsed, parsed.get("pain_level"))
            
            if ok:
                st.success("Patient record updated and session saved.")
                # Optional: Clear state after successful save
                st.session_state["v_transcript"] = ""
                st.session_state["v_parsed"] = {}
                st.rerun() # Refresh page to show clean state
            else:
                st.error("Failed to update patient.")
        else:
            st.error("No actionable data parsed from transcript.")
