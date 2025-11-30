# pdf_module.py
from fpdf import FPDF
from typing import Dict, Any, List
import json
from datetime import datetime

def create_patient_pdf(patient: Dict[str, Any], sessions: List[Dict[str, Any]], out_path: str):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(0, 10, "PYsio — Patient Summary", ln=1, align="C")
    pdf.ln(4)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Name: {patient.get('name')}", ln=1)
    pdf.cell(0, 8, f"Age / Sex: {patient.get('age')} / {patient.get('sex')}", ln=1)
    pdf.cell(0, 8, f"Surgery Date: {patient.get('surgery_date')}", ln=1)
    pdf.cell(0, 8, f"Contact: {patient.get('contact')}", ln=1)
    pdf.ln(6)

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

    pdf.output(out_path)
    return out_path
