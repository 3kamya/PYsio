# ui_voice.py
import streamlit as st
from voice_module import transcribe_uploaded_file, transcribe_microphone
from voice_parser import extract_rom_data
from datamod_sql import get_all_patients, find_patient_by_name, add_session, update_patient_fields, get_patient, get_sessions_for_patient

def voice_note_ui():
    st.header("Voice Notes — Transcribe & Auto-Fill")

    patients = get_all_patients()
    if not patients:
        st.warning("No patients found. Add a patient first in Patient Records.")
        return

    patient_map = {str(p["id"]): p for p in patients}
    options = [f"{p['id']} — {p['name']}" for p in patients]
    selected = st.selectbox("Select patient to update", options)

    # extract patient id
    pid = int(selected.split(" — ")[0])

    st.write("You can either upload an audio file, paste transcript, or do a quick microphone recording.")
    uploaded = st.file_uploader("Upload audio (wav/mp3)", type=["wav", "mp3", "m4a"])
    manual_text = st.text_area("Or paste transcript here")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Record from Microphone (short)"):
            st.info("Recording... speak now")
            transcript = transcribe_microphone()
            st.subheader("Transcript")
            st.write(transcript)
            parsed = extract_rom_data(transcript)
    with col2:
        if st.button("Transcribe Upload / Paste"):
            transcript = ""
            if uploaded:
                transcript = transcribe_uploaded_file(uploaded)
            elif manual_text:
                transcript = manual_text
            else:
                st.error("Please upload an audio file or paste text.")
                return
            st.subheader("Transcript")
            st.write(transcript)
            parsed = extract_rom_data(transcript)

    # show parsed
    if 'parsed' in locals():
        st.subheader("Parsed Values (suggested)")
        st.json(parsed)

        # build updates to patient fields (simple heuristic)
        updates = {}
        # pain
        if parsed.get("pain_level") is not None:
            updates["pain_level"] = parsed["pain_level"]
        # swelling
        if parsed.get("swelling") is not None:
            updates["swelling"] = "Yes" if parsed["swelling"]["present"] else "No"
            if parsed["swelling"].get("location"):
                updates["swelling_location"] = parsed["swelling"]["location"]
        # ROM: pick first and append into rom_entries JSON
        if parsed.get("rom"):
            # load existing rom_entries for patient
            patient = get_patient(pid)
            rom_entries = []
            if patient and patient.get("rom_entries"):
                try:
                    rom_entries = json.loads(patient.get("rom_entries"))
                except:
                    rom_entries = []
            # append each parsed rom
            for r in parsed["rom"]:
                rom_entries.append({"joint": r[0], "value": r[1]})
            updates["rom_entries"] = rom_entries
        # strength
        if parsed.get("strength"):
            patient = get_patient(pid)
            strength_entries = []
            if patient and patient.get("strength_entries"):
                try:
                    strength_entries = json.loads(patient.get("strength_entries"))
                except:
                    strength_entries = []
            for s in parsed["strength"]:
                strength_entries.append({"muscle_group": s[0], "grade": s[1]})
            updates["strength_entries"] = strength_entries

        st.markdown("**Suggested updates:**")
        st.write(updates)

        if st.button("Apply suggested updates to patient"):
            ok = update_patient_fields(pid, updates)
            if ok:
                add_session(pid, transcript, parsed, parsed.get("pain_level"))
                st.success("Patient record updated and session saved.")
            else:
                st.error("Failed to update patient.")
