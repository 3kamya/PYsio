'''#import matplotlib.pyplot as plt
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
        SELECT created_at, parsed_json, pain_level
        FROM sessions
        WHERE patient_id = ?
        ORDER BY created_at ASC;
    """

    cur.execute(query, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Parse JSON field
    df["parsed_json"] = df["parsed_json"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else {}
    )

    # Extract ROM, Strength, Swelling, Pain
    def extract_rom(p):
        if p.get("rom"):
            # Take first ROM entry per session for plotting
            return p["rom"][0]["end"]
        return None

    def extract_strength(p):
        if p.get("strength"):
            return p["strength"][0][1]
        return None

    def extract_swelling(p):
        s = p.get("swelling")
        if isinstance(s, dict):
            return 1 if s.get("present") else 0
        return None

    df["rom"] = df["parsed_json"].apply(extract_rom)
    df["strength"] = df["parsed_json"].apply(extract_strength)
    df["swelling"] = df["parsed_json"].apply(extract_swelling)
    df["pain_level"] = df["pain_level"]

    # Convert created_at to datetime
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df

# ------------------------------------------------------------
# 1. ROM Progress Plot
# ------------------------------------------------------------
def plot_rom_progress(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["rom"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["rom"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("Range of Motion (deg)")
    plt.title("ROM Progress Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"rom_progress_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

# ------------------------------------------------------------
# 2. Strength Progress Plot
# ------------------------------------------------------------
def plot_strength_progress(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["strength"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["strength"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("Strength (grade)")
    plt.title("Strength Progress Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"strength_progress_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

# ------------------------------------------------------------
# 3. Pain Trend Plot
# ------------------------------------------------------------
def plot_pain_trend(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["pain_level"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["pain_level"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("Pain Level (0–10)")
    plt.title("Pain Trend Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"pain_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

# ------------------------------------------------------------
# 4. Swelling Trend Plot
# ------------------------------------------------------------
def plot_swelling_trend(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["swelling"].isna().all():
        return None

    plt.figure()
    plt.plot(df["created_at"], df["swelling"], marker='o')
    plt.xlabel("Session Date")
    plt.ylabel("Swelling (1=Yes / 0=No)")
    plt.title("Swelling Trend Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"swelling_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

# ------------------------------------------------------------
# 5. ROM vs Strength Scatter Plot
# ------------------------------------------------------------
def plot_rom_vs_strength(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["rom"].isna().all() or df["strength"].isna().all():
        return None

    plt.figure()
    plt.scatter(df["rom"], df["strength"])
    plt.xlabel("ROM (deg)")
    plt.ylabel("Strength (grade)")
    plt.title("ROM vs Strength")
    plt.tight_layout()

    path = f"rom_vs_strength_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

# ------------------------------------------------------------
# 6. Percentage Improvement Bar Chart
# ------------------------------------------------------------
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
    plt.title("Overall Recovery Percentage")
    plt.tight_layout()

    path = f"recovery_percent_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path'''
