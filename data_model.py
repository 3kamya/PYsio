# data_model.py
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class PatientRecord:
    # Patient Information
    patient_id: str                 # assigned by data_module
    name: str
    age: int
    sex: str
    surgery_date: str               # ISO date string 'YYYY-MM-DD'
    contact: str
    surgical_procedure: str

    # Post-Operative Status
    pain_level: int                 # VAS 0-10
    swelling: bool
    swelling_location: Optional[str]
    wound_condition: str
    infection_signs: str

    # Functional Assessment
    mobility_status: str            # Walking unaided / With aid / Wheelchair / Bedridden
    bed_to_chair_transfers: str     # Independent / Assistance required
    bathing: str                    # Independent / Assistance
    dressing: str                   # Independent / Assistance
    toileting: str                  # Independent / Assistance

    # Physiotherapy Assessment (fixed 2 entries for Week 2)
    rom1_joint: Optional[str]
    rom1_active: Optional[float]
    rom1_passive: Optional[float]
    rom2_joint: Optional[str]
    rom2_active: Optional[float]
    rom2_passive: Optional[float]

    strength1_group: Optional[str]
    strength1_grade: Optional[int]  # 0-5
    strength2_group: Optional[str]
    strength2_grade: Optional[int]  # 0-5

    pain_behavior: str
    balance_gait: str

    # Home Care Treatment Plan
    ice_instructions: str
    elevation_guidelines: str
    compression_use: str

    # Exercise Program
    rom_exercises: str
    strengthening_exercises: str
    mobility_training: str

    # Safety & Fall Prevention
    home_modifications: str
    assistive_devices: str

    # Patient / Caregiver Education
    wound_care_instructions: str
    signs_to_report: str
    medication_guidelines: str

    # Progress Monitoring & Follow-up
    assessment_date: str
    followup_pain_level: Optional[int]
    followup_swelling: Optional[bool]
    rom_improvements: str
    strength_changes: str
    functional_gains: str
    next_visit: str
    additional_notes: str

    def to_dict(self):
        return asdict(self)
