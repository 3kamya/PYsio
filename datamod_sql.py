# data_module.py
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from data_model import PatientRecord, ROMEntry, StrengthEntry

DB_FILE = "pysio.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # patients table: store core patient fields, store a JSON blob for rom/strength if needed
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        sex TEXT,
        surgery_date TEXT,
        contact TEXT,
        surgical_procedure TEXT,
        pain_level INTEGER,
        swelling TEXT,
        swelling_location TEXT,
        wound_condition TEXT,
        infection_signs TEXT,
        mobility_status TEXT,
        bed_to_chair_transfers TEXT,
        bathing TEXT,
        dressing TEXT,
        toileting TEXT,
        rom_entries TEXT,
        strength_entries TEXT,
        pain_behavior TEXT,
        balance_gait TEXT,
        ice_instructions TEXT,
        elevation_guidelines TEXT,
        compression_use TEXT,
        rom_exercises TEXT,
        strengthening_exercises TEXT,
        mobility_training TEXT,
        home_modifications TEXT,
        assistive_devices TEXT,
        wound_care_instructions TEXT,
        signs_to_report TEXT,
        medication_guidelines TEXT,
        assessment_date TEXT,
        followup_pain_level INTEGER,
        followup_swelling TEXT,
        rom_improvements TEXT,
        strength_changes TEXT,
        functional_gains TEXT,
        next_visit TEXT,
        additional_notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # sessions table: for voice-note sessions
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        transcript TEXT,
        parsed_json TEXT,
        pain_level INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )
    """)
    # users table for auth
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# ---------- Patient CRUD ----------
def add_patient_from_record(rec: Dict[str, Any]) -> int:
    conn = get_conn()
    cur = conn.cursor()
    # rom_entries and strength_entries should be stored as JSON strings
    rom_json = json.dumps(rec.get("rom_entries") or [])
    strength_json = json.dumps(rec.get("strength_entries") or [])
    cur.execute("""
        INSERT INTO patients (
            name, age, sex, surgery_date, contact, surgical_procedure,
            pain_level, swelling, swelling_location, wound_condition, infection_signs,
            mobility_status, bed_to_chair_transfers, bathing, dressing, toileting,
            rom_entries, strength_entries, pain_behavior, balance_gait,
            ice_instructions, elevation_guidelines, compression_use,
            rom_exercises, strengthening_exercises, mobility_training,
            home_modifications, assistive_devices, wound_care_instructions,
            signs_to_report, medication_guidelines, assessment_date,
            followup_pain_level, followup_swelling, rom_improvements,
            strength_changes, functional_gains, next_visit, additional_notes
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        rec.get("name"), rec.get("age"), rec.get("sex"), rec.get("surgery_date"),
        rec.get("contact"), rec.get("surgical_procedure"),
        rec.get("pain_level"), rec.get("swelling"), rec.get("swelling_location"),
        rec.get("wound_condition"), rec.get("infection_signs"),
        rec.get("mobility_status"), rec.get("bed_to_chair_transfers"),
        rec.get("bathing"), rec.get("dressing"), rec.get("toileting"),
        rom_json, strength_json, rec.get("pain_behavior"), rec.get("balance_gait"),
        rec.get("ice_instructions"), rec.get("elevation_guidelines"), rec.get("compression_use"),
        rec.get("rom_exercises"), rec.get("strengthening_exercises"), rec.get("mobility_training"),
        rec.get("home_modifications"), rec.get("assistive_devices"),
        rec.get("wound_care_instructions"), rec.get("signs_to_report"), rec.get("medication_guidelines"),
        rec.get("assessment_date"), rec.get("followup_pain_level"), rec.get("followup_swelling"),
        rec.get("rom_improvements"), rec.get("strength_changes"), rec.get("functional_gains"),
        rec.get("next_visit"), rec.get("additional_notes")
    ))
    pid = cur.lastrowid
    conn.commit()
    conn.close()
    return pid

def get_all_patients() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

def get_patient(patient_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    cols = [c[0] for c in cur.description]
    conn.close()
    return dict(zip(cols, row))

def find_patient_by_name(name: str) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE name LIKE ? COLLATE NOCASE", (f"%{name}%",))
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

def update_patient_fields(patient_id: int, updates: Dict[str, Any]) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    # Build SET clause dynamically
    keys = []
    vals = []
    for k, v in updates.items():
        if k in ("rom_entries", "strength_entries"):
            vals.append(json.dumps(v))
        else:
            vals.append(v)
        keys.append(f"{k} = ?")
    if not keys:
        conn.close()
        return False
    sql = "UPDATE patients SET " + ", ".join(keys) + " WHERE id = ?"
    vals.append(patient_id)
    cur.execute(sql, tuple(vals))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed

# ---------- Sessions (voice notes) ----------
def add_session(patient_id: int, transcript: str, parsed: Dict[str, Any], pain_level: Optional[int] = None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    parsed_json = json.dumps(parsed)
    cur.execute("""
        INSERT INTO sessions (patient_id, transcript, parsed_json, pain_level) VALUES (?,?,?,?)
    """, (patient_id, transcript, parsed_json, pain_level))
    sid = cur.lastrowid
    conn.commit()
    conn.close()
    return sid

def get_sessions_for_patient(patient_id: int) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sessions WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,))
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

# ---------- Users (auth) ----------
import hashlib
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def add_user(username: str, password: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def verify_user(username: str, password: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False
    return row[0] == hash_password(password)

# Initialize DB on import
init_db()
