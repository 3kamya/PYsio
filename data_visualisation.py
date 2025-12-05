import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import json
from datetime import datetime

DB_PATH = "pysio.db"

# -----------------------------
# DATABASE CONNECTION FUNCTION
# -----------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)

# -----------------------------
# LOAD PATIENT RECORDS INTO DF
# -----------------------------
def load_patient_records(patient_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
        SELECT created_at, parsed_data, pain_level
        FROM sessions
        WHERE patient_id = ?
        ORDER BY created_at ASC;
    """

    cur.execute(query, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    # Convert to DataFrame
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Parse JSON field
    df["parsed_data"] = df["parsed_data"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else {}
    )

    # Extract ROM, Strength, Swelling, Infection Signs, Mobility
    def extract_rom(p):
        return p.get("rom_entries")[0]["end"] if p.get("rom_entries") else None

    def extract_strength(p):
        return p.get("strength_entries")[0]["grade"] if p.get("strength_entries") else None

    def extract_swelling(p):
        if p.get("swelling") == "Yes":
            return 1
        elif p.get("swelling") == "No":
            return 0
        else:
            return None

    def extract_infection(p):
        signs = p.get("infection_signs")
        return len(signs) if signs else 0

    def extract_mobility(p):
        status_list = p.get("mobility_status")
        if status_list:
            # map mobility status to numbers for plotting
            mapping = {"Poor": 1, "Limited": 2, "Normal": 3, "Excellent": 4}
            return mapping.get(status_list[0], None)
        return None

    df["rom"] = df["parsed_data"].apply(extract_rom)
    df["strength"] = df["parsed_data"].apply(extract_strength)
    df["swelling"] = df["parsed_data"].apply(extract_swelling)
    df["infection_count"] = df["parsed_data"].apply(extract_infection)
    df["mobility"] = df["parsed_data"].apply(extract_mobility)

    return df

# ============================================================
#          INDIVIDUAL VISUALIZATION FUNCTIONS
# ============================================================

def plot_rom_progress(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["rom"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["rom"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("ROM (deg)")
    plt.title("ROM Progress")
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = f"rom_progress_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def plot_strength_progress(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["strength"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["strength"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("Strength")
    plt.title("Strength Progress")
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = f"strength_progress_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def plot_pain_trend(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["pain_level"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["pain_level"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("Pain Level")
    plt.title("Pain Trend")
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = f"pain_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def plot_swelling_trend(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["swelling"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["swelling"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("Swelling (1=Yes, 0=No)")
    plt.title("Swelling Trend")
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = f"swelling_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def plot_infection_trend(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["infection_count"].isna().all():
        return None

    plt.figure()
    plt.bar(df["created_at"], df["infection_count"])
    plt.xlabel("Session Date")
    plt.ylabel("Number of Infection Signs")
    plt.title("Infection Signs Trend")
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = f"infection_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def plot_mobility_trend(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["mobility"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["mobility"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("Mobility Status (1=Poor,4=Excellent)")
    plt.title("Mobility Trend")
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = f"mobility_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def plot_rom_vs_strength(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["rom"].isna().all() or df["strength"].isna().all():
        return None

    plt.figure()
    plt.scatter(df["rom"], df["strength"])
    plt.xlabel("ROM (deg)")
    plt.ylabel("Strength")
    plt.title("ROM vs Strength")
    plt.tight_layout()
    path = f"rom_vs_strength_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

def plot_improvement_percentage(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df.shape[0] < 2:
        return None

    try:
        rom_change = ((df["rom"].iloc[-1] - df["rom"].iloc[0]) / df["rom"].iloc[0]) * 100
    except:
        rom_change = 0
    try:
        strength_change = ((df["strength"].iloc[-1] - df["strength"].iloc[0]) / df["strength"].iloc[0]) * 100
    except:
        strength_change = 0
    try:
        pain_change = -((df["pain_level"].iloc[-1] - df["pain_level"].iloc[0]) / df["pain_level"].iloc[0]) * 100
    except:
        pain_change = 0

    labels = ["ROM %", "Strength %", "Pain %"]
    values = [rom_change, strength_change, pain_change]

    plt.figure()
    plt.bar(labels, values)
    plt.ylabel("Improvement (%)")
    plt.title("Overall Recovery")
    plt.tight_layout()
    path = f"recovery_percent_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path
