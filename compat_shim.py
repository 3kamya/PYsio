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
    Shallow wrapper so main.py's name exists.
    We reuse extract_rom_data from voice_parser and wrap its output into a dict.
    """
    rom_list = extract_rom_data(text)
    return {"rom": rom_list, "raw_text": text}
