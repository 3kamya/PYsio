from fpdf import FPDF
from typing import Dict, Any, List
import json
from datetime import datetime
import os # Added os for cleanup

# Import only the active chart-generation functions
from data_visualisation import (
    plot_strength_progress,
    plot_pain_trend
)


def create_patient_pdf(patient: Dict[str, Any], sessions: List[Dict[str, Any]], out_path: str):
    """
    Creates a comprehensive PDF summary for a patient, including their details,
    session history, and key progress charts (Pain and Strength).
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 10, "PYsio Patient Summary", ln=1, align="C")
    pdf.ln(4)

    # -------------------------------
    # Patient Info Section
    # -------------------------------
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Name: {patient.get('name')}", ln=1)
    pdf.cell(0, 8, f"Age / Sex: {patient.get('age')} / {patient.get('sex')}", ln=1)
    pdf.cell(0, 8, f"Surgery Date: {patient.get('surgery_date')}", ln=1)
    pdf.cell(0, 8, f"Contact: {patient.get('contact')}", ln=1)
    pdf.ln(6)

    # -------------------------------
    # Recent Sessions Section
    # -------------------------------
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 8, "Recent Sessions:", ln=1)
    pdf.set_font("Arial", size=11)

    if not sessions:
        pdf.cell(0, 6, "No sessions recorded.", ln=1)
    else:
        # Display up to 10 recent sessions
        for s in sessions[:10]:
            # Convert timestamp to a readable format if necessary
            created = s.get("created_at", "")
            
            # Use 'transcript' if available, otherwise just note the session date
            transcript_text = s.get('transcript', 'Manual session entry.')
            if len(transcript_text) > 80:
                transcript_text = transcript_text[:77] + "..." # Truncate long notes

            pdf.multi_cell(0, 6, f"Session Date: {created}\nNote: {transcript_text}")
            
            # Display pain level if available
            if s.get("pain_level"):
                pdf.set_font("Arial", size=10, style="I")
                # Removed U+00A0 from indentation
                pdf.cell(0, 5, f"  Pain Level: {s['pain_level']}", ln=1) 
                pdf.set_font("Arial", size=11)
            
            pdf.ln(1) # Small space between sessions

    pdf.ln(6)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8,
              f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
              ln=1)

    # -------------------------------
    # Generate and Insert Charts
    # -------------------------------
    chart_paths = []

    # 1. Pain Trend Plot
    # FIX: Using 'id' instead of 'patient_id' for the single patient dictionary
    pain_path = plot_pain_trend(patient["id"]) 
    if pain_path: chart_paths.append(("Pain Trend Over Sessions", pain_path))

    # 2. Strength Progress Plot
    # FIX: Using 'id' instead of 'patient_id' for the single patient dictionary
    strength_path = plot_strength_progress(patient["id"]) 
    if strength_path: chart_paths.append(("Strength Progress Over Sessions", strength_path))

    
    # Insert charts into PDF and clean up files
    for title, img_path in chart_paths:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, title, ln=1)
        # Use w=180 to fit the chart nicely on an A4 page
        pdf.image(img_path, x=15, y=None, w=180)
        
        # Clean up the generated image file immediately after insertion
        try:
            os.remove(img_path)
        except OSError as e:
            print(f"Error removing temporary chart file {img_path}: {e}")

    # Final output
    pdf.output(out_path)
    return out_path
