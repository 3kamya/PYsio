import matplotlib.pyplot as plt
import psycopg2
import pandas as pd
from datetime import datetime

# -----------------------------
# DATABASE CONNECTION FUNCTION
# -----------------------------
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="physio_db",
        user="postgres",
        password="yourpassword"
    )

# -----------------------------
# LOAD PATIENT RECORDS INTO DF
# -----------------------------
def load_patient_records(patient_id):
    conn = get_connection()
    query = """
        SELECT session_date, rom, strength, pain_level, swelling
        FROM patient_records
        WHERE patient_id = %s
        ORDER BY session_date ASC;
    """
    df = pd.read_sql(query, conn, params=(patient_id,))
    conn.close()
    return df

# ============================================================
#           INDIVIDUAL VISUALIZATION FUNCTIONS
# ============================================================

# ------------------------------------------------------------
# 1. ROM Progress Plot
# ------------------------------------------------------------
def plot_rom_progress(patient_id):
    df = load_patient_records(patient_id)
    plt.figure()
    plt.plot(df["session_date"], df["rom"])
    plt.xlabel("Session Date")
    plt.ylabel("Range of Motion (deg)")
    plt.title("ROM Progress Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"rom_progress_{patient_id}.png")
    plt.close()
    return f"rom_progress_{patient_id}.png"

# ------------------------------------------------------------
# 2. Strength Progress Plot
# ------------------------------------------------------------
def plot_strength_progress(patient_id):
    df = load_patient_records(patient_id)
    plt.figure()
    plt.plot(df["session_date"], df["strength"])
    plt.xlabel("Session Date")
    plt.ylabel("Strength (N or kg)")
    plt.title("Strength Progress Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"strength_progress_{patient_id}.png")
    plt.close()
    return f"strength_progress_{patient_id}.png"

# ------------------------------------------------------------
# 3. Pain Trend Plot
# ------------------------------------------------------------
def plot_pain_trend(patient_id):
    df = load_patient_records(patient_id)
    plt.figure()
    plt.plot(df["session_date"], df["pain_level"])
    plt.xlabel("Session Date")
    plt.ylabel("Pain Level (0–10)")
    plt.title("Pain Trend Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"pain_trend_{patient_id}.png")
    plt.close()
    return f"pain_trend_{patient_id}.png"

# ------------------------------------------------------------
# 4. Swelling Trend Plot
# ------------------------------------------------------------
def plot_swelling_trend(patient_id):
    df = load_patient_records(patient_id)
    plt.figure()
    plt.plot(df["session_date"], df["swelling"])
    plt.xlabel("Session Date")
    plt.ylabel("Swelling (cm or mm)")
    plt.title("Swelling Trend Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"swelling_trend_{patient_id}.png")
    plt.close()
    return f"swelling_trend_{patient_id}.png"

# ------------------------------------------------------------
# 5. Histogram of Pain Levels
# ------------------------------------------------------------
def plot_pain_histogram(patient_id):
    df = load_patient_records(patient_id)
    plt.figure()
    plt.hist(df["pain_level"])
    plt.xlabel("Pain Level")
    plt.ylabel("Frequency")
    plt.title("Distribution of Pain Levels")
    plt.tight_layout()
    plt.savefig(f"pain_hist_{patient_id}.png")
    plt.close()
    return f"pain_hist_{patient_id}.png"

# ------------------------------------------------------------
# 6. ROM vs Strength Scatter Plot
# ------------------------------------------------------------
def plot_rom_vs_strength(patient_id):
    df = load_patient_records(patient_id)
    plt.figure()
    plt.scatter(df["rom"], df["strength"])
    plt.xlabel("ROM (deg)")
    plt.ylabel("Strength")
    plt.title("ROM vs Strength")
    plt.tight_layout()
    plt.savefig(f"rom_vs_strength_{patient_id}.png")
    plt.close()
    return f"rom_vs_strength_{patient_id}.png"

# ------------------------------------------------------------
# 7. Percentage Improvement Bar Chart
# ------------------------------------------------------------
def plot_improvement_percentage(patient_id):
    df = load_patient_records(patient_id)

    if df.shape[0] < 2:
        return None

    rom_change = ((df["rom"].iloc[-1] - df["rom"].iloc[0]) / df["rom"].iloc[0]) * 100
    strength_change = ((df["strength"].iloc[-1] - df["strength"].iloc[0]) / df["strength"].iloc[0]) * 100
    pain_change = -((df["pain_level"].iloc[-1] - df["pain_level"].iloc[0]) / df["pain_level"].iloc[0]) * 100

    labels = ["ROM %", "Strength %", "Pain %"]
    values = [rom_change, strength_change, pain_change]

    plt.figure()
    plt.bar(labels, values)
    plt.ylabel("Improvement (%)")
    plt.title("Overall Recovery Percentage")
    plt.tight_layout()
    plt.savefig(f"recovery_percent_{patient_id}.png")
    plt.close()
    return f"recovery_percent_{patient_id}.png"
