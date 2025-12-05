import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import json
from datetime import datetime

# Define the database path
DB_PATH = "pysio.db"

# -----------------------------
# DATABASE CONNECTION FUNCTION
# -----------------------------
def get_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

# -----------------------------
# LOAD PATIENT RECORDS INTO DF
# -----------------------------
def load_patient_records(patient_id):
    """
    Loads all session records for a patient, parses the necessary data,
    and returns a DataFrame suitable for visualization.
    """
    conn = get_connection()
    # Use Row factory to access columns by name like a dictionary
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # NOTE: Assuming 'parsed_json' and 'pain_level' columns exist in the 'sessions' table.
    query = """
        SELECT created_at, parsed_json, pain_level
        FROM sessions
        WHERE patient_id = ?
        ORDER BY created_at ASC;
    """

    # Ensure patient_id is an integer for the query
    cur.execute(query, (int(patient_id),))
    rows = cur.fetchall()
    conn.close()

    # Convert list of sqlite.Row objects to a list of dictionaries for robust DataFrame creation
    data = [dict(row) for row in rows]
    df = pd.DataFrame(data)

    if df.empty:
        return df

    # Parse JSON field. This handles the KeyError by ensuring the column is accessed correctly.
    df["parsed_json"] = df["parsed_json"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else {}
    )

    # --- Data Extraction Helpers ---

    def extract_strength(p):
        """
        Extracts the grade of the first strength entry.
        FIXED: Accessing ['grade'] key instead of array index [1].
        """
        if p.get("strength") and p["strength"][0].get("grade") is not None:
            # Strength is an array of dicts: [{"muscle_group": "quads", "grade": 4}]
            return p["strength"][0]["grade"]
        return None

    # Apply extraction
    df["strength"] = df["parsed_json"].apply(extract_strength)

    # Clean up pain level (ensure it's numeric)
    df["pain_level"] = pd.to_numeric(df["pain_level"], errors='coerce')

    # Create a simple session number index for the X-axis
    df["session_number"] = range(1, len(df) + 1)
    
    return df.dropna(subset=['session_number']) # Ensure we only plot valid sessions

# ------------------------------------------------------------
# 1. Pain Trend Plot (0-10)
# ------------------------------------------------------------
def plot_pain_trend(patient_id):
    """Generates a line plot of pain level over successive sessions."""
    df = load_patient_records(patient_id)
    
    # Filter for records that actually contain pain data
    df_plot = df.dropna(subset=["pain_level"])

    if df_plot.empty:
        return None

    plt.figure(figsize=(8, 4))
    plt.plot(df_plot["session_number"], df_plot["pain_level"], 
             marker='o', linestyle='-', color='#C0392B', linewidth=2)
    
    plt.xlabel("Session Number", fontsize=12)
    plt.ylabel("Pain Level (0-10)", fontsize=12)
    plt.title(f"Patient {patient_id} Pain Trend by Session", fontsize=14, fontweight='bold')
    
    # Set Y-axis limits for consistency (0 to 10)
    plt.yticks(range(0, 11, 2))
    plt.ylim(0, 10.5) 

    # Set X-axis ticks to match session numbers
    plt.xticks(df_plot["session_number"])
    
    plt.grid(True, which='major', linestyle='--', alpha=0.6)
    plt.tight_layout()

    path = f"pain_trend_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

# ------------------------------------------------------------
# 2. Strength Progress Plot (Manual Muscle Test Grade)
# ------------------------------------------------------------
def plot_strength_progress(patient_id):
    """Generates a line plot of strength grade over successive sessions."""
    df = load_patient_records(patient_id)
    
    # Filter for records that actually contain strength data
    df_plot = df.dropna(subset=["strength"])

    if df_plot.empty:
        return None

    plt.figure(figsize=(8, 4))
    plt.plot(df_plot["session_number"], df_plot["strength"], 
             marker='s', linestyle='-', color='#2980B9', linewidth=2)
    
    plt.xlabel("Session Number", fontsize=12)
    plt.ylabel("Strength Grade (0-5)", fontsize=12)
    plt.title(f"Patient {patient_id} Strength Progress by Session", fontsize=14, fontweight='bold')
    
    # Set Y-axis limits and labels for consistency (0 to 5 MMT grades)
    plt.yticks(range(0, 6)) 
    plt.ylim(0, 5.5) 
    
    # Set X-axis ticks to match session numbers
    plt.xticks(df_plot["session_number"])
    
    plt.grid(True, which='major', linestyle='--', alpha=0.6)
    plt.tight_layout()

    path = f"strength_progress_{patient_id}.png"
    plt.savefig(path)
    plt.close()
    return path

