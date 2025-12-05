'''import csv
import os
from data_model import PatientRecord

CSV_FILE = "patient_records.csv"

def save_record(record: PatientRecord):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
      
        if not file_exists:
            writer.writerow([
                "Name", "Age", "Sex", "Surgery Date", "Contact", "Surgical Procedure",
                "Pain Level", "Swelling", "Swelling Location", "Wound Condition", "Infection Signs",
                "Mobility Status", "Transfer Status", "Bathing", "Dressing", "Toileting",
                "ROM Entries", "Strength Entries",
                "Pain Behavior", "Balance/Gait",
                "Ice", "Elevation", "Compression",
                "ROM Exercises", "Strength Exercises", "Mobility Training",
                "Home Modifications", "Assistive Devices",
                "Wound Care", "Signs to Report", "Medication Instructions",
                "Assessment Date", "Followup Pain", "Followup Swelling",
                "ROM Improvements", "Strength Changes", "Functional Gains",
                "Next Visit", "Additional Notes"
            ])

        writer.writerow([
            record.name, record.age, record.sex, record.surgery_date, record.contact, record.surgical_procedure,
            record.pain_level, record.swelling, record.swelling_location, record.wound_condition, record.infection_signs,
            record.mobility_status, record.transfer_status, record.bathing, record.dressing, record.toileting,
            "; ".join([f"{r.joint} (A:{r.active_rom}, P:{r.passive_rom})" for r in record.rom_entries]),
            "; ".join([f"{s.muscle_group}:{s.grade}" for s in record.strength_entries]),
            record.pain_behavior, record.balance_gait,
            record.ice_instructions, record.elevation_guidelines, record.compression_use,
            record.rom_exercises, record.strength_exercises, record.mobility_training,
            record.home_modifications, record.assistive_devices,
            record.wound_care, record.report_signs, record.medications,
            record.assessment_date, record.followup_pain_level, record.followup_swelling,
            record.rom_improvements, record.strength_changes, record.functional_gains,
            record.next_visit, record.additional_notes
        ])


def load_records():
    if not os.path.isfile(CSV_FILE):
        return []'''

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
