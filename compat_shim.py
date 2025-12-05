# compat_shim.py
"""
Compatibility shim to expose the names main.py expects while using your existing datamod_sql,
pdf_export, voice_text, voice_parser implementations.
"""

import os
import json
import tempfile
from typing import Optional
import pandas as pd

# datamod_sql functions
from datamod_sql import (
    add_patient_from_record,
    get_all_patients,
    get_patient,
    get_sessions_for_patient,
    add_session,
    update_patient_fields,
    init_db
)

# voice / parser
from voice_module import transcribe_microphone
from voice_module import transcribe_uploaded_file  # used for uploaded files
from voice_parser import extract_rom_data

# pdf export
from pdf_export import create_patient_pdf

# Make sure DB initialized
init_db()


# ---------- DB API expected by main.py ----------
def save_record_sql(record_dict: dict) -> int:
    """
    main.py expects save_record_sql(record) -> id
    Our underlying function is add_patient_from_record(rec)
    """
    return add_patient_from_record(record_dict)


def load_all_patients_sql() -> pd.DataFrame:
    """
    Return a pandas DataFrame similar to what main.py expects.
    Convert internal 'id' column -> 'patient_id' for consistency.
    """
    rows = get_all_patients()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    # normalize id -> patient_id
    if "id" in df.columns and "patient_id" not in df.columns:
        df = df.rename(columns={"id": "patient_id"})
    # normalize follow-up pain column name differences
    if "follow_pain" in df.columns and "followup_pain_level" not in df.columns:
        df = df.rename(columns={"follow_pain": "followup_pain_level"})
    # ensure patient_id type is consistent
    df["patient_id"] = df["patient_id"].astype(str)
    return df


def load_single_patient_sql(patient_id) -> dict:
    # Accept numeric or string id
    try:
        pid = int(patient_id)
    except:
        pid = int(str(patient_id))
    return get_patient(pid)


# ---------- PDF wrapper ----------
def generate_patient_pdf(patient_id: int) -> str:
    """
    Creates PDF using existing create_patient_pdf function.
    Returns path to pdf.
    """
    pid = int(patient_id)
    patient = get_patient(pid)
    sessions = get_sessions_for_patient(pid)
    out_path = f"patient_{pid}_summary.pdf"
    create_patient_pdf(patient, sessions, out_path)
    return out_path


# ---------- Voice wrapper ----------
def convert_voice_to_text(uploaded_file_or_none: Optional[object] = None) -> str:
    """
    If uploaded_file_or_none is None -> use microphone helper transcribe_voice().
    If it's a file-like object from Streamlit -> use transcribe_uploaded_file from voice_module.
    """
    try:
        if uploaded_file_or_none is None:
            return transcribe_voice()
        # otherwise assume streamlit UploadedFile or path-like
        return transcribe_uploaded_file(uploaded_file_or_none)
    except Exception as e:
        return f"[transcription error] {e}"


def extract_structured_keywords(text: str) -> dict:
    """
    Converts voice_parser output into the structure main.py expects.
    """
    parsed_list = extract_rom_data(text)

    result = {
        "rom_entries": [],
        "strength_entries": [],
        "swelling": None,
        "pain_level": None,
        "infection_signs": [],
        "mobility_status": None,
        "raw_text": text
    }

    for entry in parsed_list:
        typ = entry.get("type")
        if typ == "rom":
            # main.py expects a JSON string with "joint", "start", "end"
            result["rom_entries"].append({
                "joint": entry.get("rom_type"),
                "start": entry.get("start"),
                "end": entry.get("end")
            })
        elif typ == "pain_level":
            result["pain_level"] = entry.get("pain_level")
        elif typ == "swelling":
            result["swelling"] = entry.get("present")
        elif typ == "infection_signs":
            result["infection_signs"] = entry.get("signs", [])
        elif typ == "mobility_status":
            result["mobility_status"] = entry.get("status")
        elif typ == "strength":
            result["strength_entries"].append({
                "muscle": entry.get("muscle"),
                "grade": entry.get("grade")
            })

    # Convert lists to JSON strings if main.py expects that
    if result["rom_entries"]:
        import json
        result["rom_entries"] = json.dumps(result["rom_entries"])
    if result["strength_entries"]:
        import json
        result["strength_entries"] = json.dumps(result["strength_entries"])

    return result
