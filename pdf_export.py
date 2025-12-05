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

    # Generate visualisation charts
    rom_path = plot_rom_progress(patient["patient_id"])
    strength_path = plot_strength_progress(patient["patient_id"])
    pain_path = plot_pain_trend(patient["patient_id"])
    swelling_path = plot_swelling_trend(patient["patient_id"])
    hist_path = plot_pain_histogram(patient["patient_id"])
    scatter_path = plot_rom_vs_strength(patient["patient_id"])
    improve_path = plot_improvement_percentage(patient["patient_id"])

    # Optional: add charts to report using ReportLab
    # story.append(Paragraph("DATA VISUALISATION", heading_style))
    # story.append(Spacer(1, 12))
    # chart_paths = [
    #     ("ROM Progress", rom_path),
    #     ("Strength Progress", strength_path),
    #     ("Pain Trend", pain_path),
    #     ("Swelling Trend", swelling_path),
    #     ("Pain Histogram", hist_path),
    #     ("ROM vs Strength", scatter_path),
    #     ("Recovery Percentage", improve_path)
    # ]
    # for title, img_path in chart_paths:
    #     if img_path:
    #         story.append(Paragraph(title, normal_style))
    #         story.append(Image(img_path, width=400, height=300))
    #         story.append(Spacer(1, 24))

    pdf.output(out_path)
    return out_path
