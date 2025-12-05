# compat_shim.py
"""
Compatibility shim to expose the names main.py expects while using your existing datamod_sql,
pdf_export, voice_module, voice_parser implementations.
"""

import json
import pandas as pd
from typing import Optional

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
from voice_module import transcribe_microphone, transcribe_uploaded_file
from voice_parser import extract_rom_data
from ui_voice import normalize_parsed

# pdf export
from pdf_export import create_patient_pdf

# Initialize DB
init_db()


# ---------- DB API expected by main.py ----------
def save_record_sql(record_dict: dict) -> int:
    """
    main.py expects save_record_sql(record) -> id
    """
    return add_patient_from_record(record_dict)


def load_all_patients_sql() -> pd.DataFrame:
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
    df["patient_id"] = df["patient_id"].astype(str)
    return df


def load_single_patient_sql(patient_id) -> dict:
    try:
        pid = int(patient_id)
    except:
        pid = int(str(patient_id))
    return get_patient(pid)


# ---------- PDF wrapper ----------
def generate_patient_pdf(patient_id: int) -> str:
    pid = int(patient_id)
    patient = get_patient(pid)
    sessions = get_sessions_for_patient(pid)
    out_path = f"patient_{pid}_summary.pdf"
    create_patient_pdf(patient, sessions, out_path)
    return out_path


# ---------- Voice wrapper ----------
def convert_voice_to_text(uploaded_file_or_none: Optional[object] = None) -> str:
    """
    If uploaded_file_or_none is None -> use microphone.
    If it's a file-like object from Streamlit -> use transcribe_uploaded_file.
    """
    try:
        if uploaded_file_or_none is None:
            return transcribe_microphone()
        return transcribe_uploaded_file(uploaded_file_or_none)
    except Exception as e:
        return f"[transcription error] {e}"


def extract_structured_keywords(text: str) -> dict:
    """
    Converts voice_parser output into normalized dict expected by ui_voice.py.
    Guarantees actionable data is recognized.
    """
    parsed_list = extract_rom_data(text)
    normalized = normalize_parsed(parsed_list)

    # Add raw_text for reference
    normalized["raw_text"] = text

    # Ensure keys exist even if empty
    for key in ["rom", "strength", "swelling", "pain_level", "infection_signs", "mobility_status"]:
        if key not in normalized:
            normalized[key] = None if key in ["swelling", "pain_level"] else []

    return normalized
