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
        SELECT date, parsed_data, pain_level
        FROM sessions
        WHERE patient_id = ?
        ORDER BY date ASC;
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

    # Extract ROM, Strength, Swelling from parsed_data
    df["rom"] = df["parsed_data"].apply(lambda p: p.get("rom")[0][1] if p.get("rom") else None)
    df["strength"] = df["parsed_data"].apply(lambda p: p.get("strength")[0][1] if p.get("strength") else None)
    df["swelling"] = df["parsed_data"].apply(lambda p: p["swelling"]["present"] if p.get("swelling") else None)

    return df

# ============================================================
#           INDIVIDUAL VISUALIZATION FUNCTIONS
# ============================================================

# ------------------------------------------------------------
# 1. ROM Progress Plot
# ------------------------------------------------------------
def plot_rom_progress(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["rom"].isna().all():
        return None

    plt.figure()
    plt.plot(df["date"], df["rom"])
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
    plt.plot(df["date"], df["strength"])
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
    plt.plot(df["date"], df["pain_level"])
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
    plt.plot(df["date"], df["swelling"])
    plt.xlabel("Session Date")
    plt.ylabel("Swelling (Present=1 / Absent=0)")
    plt.title("Swelling Trend Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"swelling_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

# ------------------------------------------------------------
# 5. Histogram of Pain Levels
# ------------------------------------------------------------
def plot_pain_histogram(patient_id):
    df = load_patient_records(patient_id)
    if df.empty or df["pain_level"].isna().all():
        return None

    plt.figure()
    plt.hist(df["pain_level"])
    plt.xlabel("Pain Level")
    plt.ylabel("Frequency")
    plt.title("Distribution of Pain Levels")
    plt.tight_layout()

    path = f"pain_hist_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

# ------------------------------------------------------------
# 6. ROM vs Strength Scatter Plot
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
# 7. Percentage Improvement Bar Chart
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
    return path
