# data_module.py
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

DB_FILE = "pysio.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # patients table
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
    # sessions table
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
    # users table
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
    """
    Dynamically insert a patient record based on current DB columns.
    """
    conn = get_conn()
    cur = conn.cursor()

    # get current columns in patients table
    cur.execute("PRAGMA table_info(patients)")
    columns_info = cur.fetchall()
    columns = [col[1] for col in columns_info if col[1] not in ("id", "created_at")]

    values = []
    for col in columns:
        if col in ("rom_entries", "strength_entries"):
            values.append(json.dumps(rec.get(col) or []))
        else:
            values.append(rec.get(col))

    placeholders = ",".join(["?"] * len(columns))
    sql = f"INSERT INTO patients ({', '.join(columns)}) VALUES ({placeholders})"

    cur.execute(sql, tuple(values))
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
    conn.close()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
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

# ---------- Sessions ----------
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

# ---------- Users ----------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def add_user(username: str, password: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hash_password(password)))
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
