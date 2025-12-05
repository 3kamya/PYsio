# pdf_export.py
from fpdf import FPDF
from typing import Dict, Any, List
import json
from datetime import datetime
from data_visualisation import (
    plot_rom_progress,
    plot_strength_progress,
    plot_pain_trend,
    plot_swelling_trend,
    plot_pain_histogram,
    plot_rom_vs_strength,
    plot_improvement_percentage
)
from reportlab.platypus import Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_patient_pdf(patient: Dict[str, Any], sessions: List[Dict[str, Any]], out_path: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 10, "PYsio — Patient Summary", ln=1, align="C")
    pdf.ln(4)

    # Patient Info
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Name: {patient.get('name')}", ln=1)
    pdf.cell(0, 8, f"Age / Sex: {patient.get('age')} / {patient.get('sex')}", ln=1)
    pdf.cell(0, 8, f"Surgery Date: {patient.get('surgery_date')}", ln=1)
    pdf.cell(0, 8, f"Contact: {patient.get('contact')}", ln=1)
    pdf.ln(6)

    # Recent Sessions
    pdf.set_font("Arial", size=12, style="B")
    pdf.cell(0, 8, "Recent Sessions:", ln=1)
    pdf.set_font("Arial", size=11)

    if not sessions:
        pdf.cell(0, 6, "No sessions recorded.", ln=1)
    else:
        for s in sessions[:10]:
            created = s.get("created_at", "")
            pdf.multi_cell(0, 6, f"- {created}: {s.get('transcript')}")
            parsed = s.get("parsed_json")
            if parsed:
                try:
                    parsed_obj = json.loads(parsed)
                except:
                    parsed_obj = parsed
                pdf.set_font("Arial", size=10)
                pdf.multi_cell(0, 5, f"  Parsed: {parsed_obj}")
                pdf.set_font("Arial", size=11)
            pdf.ln(1)

    pdf.ln(6)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1)

    # -------------------------------
    # Generate visualisation charts
    # -------------------------------
    chart_paths = []

    # Each function returns a path to the saved PNG
    rom_path = plot_rom_progress(patient["patient_id"])
    if rom_path: chart_paths.append(("ROM Progress", rom_path))

    strength_path = plot_strength_progress(patient["patient_id"])
    if strength_path: chart_paths.append(("Strength Progress", strength_path))

    pain_path = plot_pain_trend(patient["patient_id"])
    if pain_path: chart_paths.append(("Pain Trend", pain_path))

    swelling_path = plot_swelling_trend(patient["patient_id"])
    if swelling_path: chart_paths.append(("Swelling Trend", swelling_path))

    hist_path = plot_pain_histogram(patient["patient_id"])
    if hist_path: chart_paths.append(("Pain Histogram", hist_path))

    scatter_path = plot_rom_vs_strength(patient["patient_id"])
    if scatter_path: chart_paths.append(("ROM vs Strength", scatter_path))

    improve_path = plot_improvement_percentage(patient["patient_id"])
    if improve_path: chart_paths.append(("Recovery Percentage", improve_path))

    # Add charts to PDF
    styles = getSampleStyleSheet()
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    for title, img_path in chart_paths:
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, title, ln=1)
        pdf.image(img_path, x=15, y=None, w=180)
    
    pdf.output(out_path)
    return out_path
