import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import json
from datetime import datetime

DB_PATH = "pysio.db"

# -----------------------------
# DB CONNECTION
# -----------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)


# ============================================================
#                 1) LOAD SESSION DATA (pain, swelling)
# ============================================================
def load_session_data(patient_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
        SELECT timestamp, parsed_data, pain_level
        FROM sessions
        WHERE patient_id = ?
        ORDER BY timestamp ASC;
    """

    cur.execute(query, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Parse JSON
    df["parsed_data"] = df["parsed_data"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else {}
    )

    # Extract swelling from parsed_data
    df["swelling"] = df["parsed_data"].apply(
        lambda p: 1 if (p.get("swelling") and p["swelling"].get("present")) else 0
    )

    return df


# ============================================================
#                 2) LOAD ROM PROGRESS
# ============================================================
def load_rom_progress(patient_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
        SELECT joint, start, end, timestamp
        FROM rom_progress
        WHERE patient_id = ?
        ORDER BY timestamp ASC;
    """

    cur.execute(query, (patient_id,))
    rows = cur.fetchall()
    conn.close()

    df = pd.DataFrame(rows)

    return df


# ============================================================
#                        PLOTS
# ============================================================

# ------------------------------------------------------------
# ROM PROGRESS PLOT
# ------------------------------------------------------------
def plot_rom_progress(patient_id):
    df = load_rom_progress(patient_id)
    if df.empty:
        return None

    # Take END value (actual measured ROM)
    df["rom_value"] = df["end"]

    plt.figure()
    plt.plot(df["timestamp"], df["rom_value"], marker="o")
    plt.xlabel("Session Date")
    plt.ylabel("ROM (degrees)")
    plt.title(f"ROM Progress — {df['joint'].iloc[0]}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"rom_progress_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path


# ------------------------------------------------------------
# STRENGTH PROGRESS — (PATIENT TABLE)
# ------------------------------------------------------------
def plot_strength_progress(patient_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT strength_entries FROM patients WHERE id = ?", (patient_id,))
    row = cur.fetchone()
    conn.close()

    if not row or not row[0]:
        return None

    entries = json.loads(row[0])

    if not entries:
        return None

    df = pd.DataFrame(entries)

    if df.empty:
        return None

    plt.figure()
    plt.plot(df.index, df["grade"], marker="o")
    plt.xlabel("Session")
    plt.ylabel("Strength Grade")
    plt.title("Strength Progress")
    plt.tight_layout()

    path = f"strength_progress_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path


# ------------------------------------------------------------
# PAIN TREND
# ------------------------------------------------------------
def plot_pain_trend(patient_id):
    df = load_session_data(patient_id)
    if df.empty or df["pain_level"].isna().all():
        return None

    plt.figure()
    plt.plot(df["timestamp"], df["pain_level"], marker="o")
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
# SWELLING TREND
# ------------------------------------------------------------
def plot_swelling_trend(patient_id):
    df = load_session_data(patient_id)
    if df.empty:
        return None

    plt.figure()
    plt.plot(df["timestamp"], df["swelling"], marker="o")
    plt.xlabel("Session Date")
    plt.ylabel("Swelling (1=Present, 0=No)")
    plt.title("Swelling Trend")
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = f"swelling_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path


# ------------------------------------------------------------
# PAIN HISTOGRAM
# ------------------------------------------------------------
def plot_pain_histogram(patient_id):
    df = load_session_data(patient_id)
    if df.empty or df["pain_level"].isna().all():
        return None

    plt.figure()
    plt.hist(df["pain_level"])
    plt.xlabel("Pain Level")
    plt.ylabel("Frequency")
    plt.title("Pain Distribution")
    plt.tight_layout()

    path = f"pain_hist_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path


# ------------------------------------------------------------
# ROM vs STRENGTH SCATTER
# ------------------------------------------------------------
def plot_rom_vs_strength(patient_id):
    rom_df = load_rom_progress(patient_id)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT strength_entries FROM patients WHERE id = ?", (patient_id,))
    row = cur.fetchone()
    conn.close()

    if not row or not row[0]:
        return None

    strength_df = pd.DataFrame(json.loads(row[0]))

    if rom_df.empty or strength_df.empty:
        return None

    min_len = min(len(rom_df), len(strength_df))
    rom_df = rom_df.head(min_len)
    strength_df = strength_df.head(min_len)

    plt.figure()
    plt.scatter(rom_df["end"], strength_df["grade"])
    plt.xlabel("ROM (deg)")
    plt.ylabel("Strength Grade")
    plt.title("ROM vs Strength")
    plt.tight_layout()

    path = f"rom_vs_strength_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path


# ------------------------------------------------------------
# IMPROVEMENT % BAR GRAPH
# ------------------------------------------------------------
def plot_improvement_percentage(patient_id):
    rom_df = load_rom_progress(patient_id)
    sess_df = load_session_data(patient_id)

    if rom_df.empty or sess_df.empty:
        return None

    try:
        rom_change = ((rom_df["end"].iloc[-1] - rom_df["end"].iloc[0]) / rom_df["end"].iloc[0]) * 100
    except:
        rom_change = 0

    try:
        pain_change = -((sess_df["pain_level"].iloc[-1] - sess_df["pain_level"].iloc[0]) / sess_df["pain_level"].iloc[0]) * 100
    except:
        pain_change = 0

    labels = ["ROM %", "Pain %"]
    values = [rom_change, pain_change]

    plt.figure()
    plt.bar(labels, values)
    plt.ylabel("Improvement (%)")
    plt.title("Overall Improvement")
    plt.tight_layout()

    path = f"recovery_percent_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path
