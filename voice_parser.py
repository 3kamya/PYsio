# voice_parser.py
import re

# -----------------------------
# Keywords / phrases your system can understand
# -----------------------------
ROM_KEYWORDS = {
    "knee flexion": "knee_flexion",
    "knee extension": "knee_extension",
    "shoulder flexion": "shoulder_flexion",
    "shoulder abduction": "shoulder_abduction",
    "external rotation": "external_rotation",
    "internal rotation": "internal_rotation",
    "hip flexion": "hip_flexion",
    "hip extension": "hip_extension",
    "elbow flexion": "elbow_flexion",
    "elbow extension": "elbow_extension"
}

# Swelling keywords
SWELLING_KEYWORDS = ["swelling", "edema", "effusion"]

# Pain keywords
PAIN_KEYWORDS = ["pain", "ache", "discomfort", "soreness"]

# Infection / signs
INFECTION_KEYWORDS = ["redness", "pus", "infection", "warmth"]

# Mobility / status
MOBILITY_KEYWORDS = ["walk", "mobility", "stand", "sit", "climb", "move"]

# -----------------------------
# Helper functions
# -----------------------------
def detect_rom_type(text):
    text = text.lower()
    for keyword in ROM_KEYWORDS:
        if keyword in text:
            return ROM_KEYWORDS[keyword], keyword
    return None, None

def contains_keyword(text, keywords):
    text = text.lower()
    for kw in keywords:
        if kw in text:
            return kw
    return None

# -----------------------------
# Main extraction function
# -----------------------------
def extract_rom_data(transcript):
    transcript = transcript.lower()
    results = []

    sentences = re.split(r'[.,;]', transcript)
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        entry = {}

        # -----------------------------
        # ROM extraction
        # -----------------------------
        rom_code, rom_phrase = detect_rom_type(sentence)
        if rom_code:
            entry["type"] = "rom"
            entry["rom_type"] = rom_code
            entry["rom_phrase"] = rom_phrase

            # Patterns
            match_range = re.search(r'from\s+(\d+)\s+to\s+(\d+)\s*degrees?', sentence)
            match_around = re.search(r'around\s+(\d+)\s*degrees?', sentence)
            match_improve = re.search(r"(improved|increased|reduced).*?(\d+)\s*degrees?", sentence)
            match_single = re.search(r'(\d+)\s*degrees?', sentence)

            if match_range:
                entry["start"] = int(match_range.group(1))
                entry["end"] = int(match_range.group(2))
            elif match_around:
                entry["start"] = None
                entry["end"] = int(match_around.group(1))
            elif match_improve:
                entry["start"] = None
                entry["end"] = int(match_improve.group(2))
            elif match_single:
                entry["start"] = None
                entry["end"] = int(match_single.group(1))
            else:
                entry["start"] = None
                entry["end"] = None

            results.append(entry)
            continue  # skip other checks if ROM found

        # -----------------------------
        # Swelling extraction
        # -----------------------------
        if contains_keyword(sentence, SWELLING_KEYWORDS):
            entry["type"] = "swelling"
            entry["present"] = True
            match_amount = re.search(r'(\d+)\s*(cm|centimeters?)', sentence)
            if match_amount:
                entry["amount"] = int(match_amount.group(1))
                entry["unit"] = "cm"
            results.append(entry)
            continue

        # -----------------------------
        # Pain level extraction
        # -----------------------------
        if contains_keyword(sentence, PAIN_KEYWORDS):
            entry["type"] = "pain_level"
            match_val = re.search(r'(\d+)\s*(/10)?', sentence)
            if match_val:
                entry["pain_level"] = int(match_val.group(1))
            else:
                entry["pain_level"] = None
            results.append(entry)
            continue

        # -----------------------------
        # Signs of infection
        # -----------------------------
        if contains_keyword(sentence, INFECTION_KEYWORDS):
            entry["type"] = "infection_signs"
            entry["signs"] = [kw for kw in INFECTION_KEYWORDS if kw in sentence]
            results.append(entry)
            continue

        # -----------------------------
        # Mobility status
        # -----------------------------
        if contains_keyword(sentence, MOBILITY_KEYWORDS):
            entry["type"] = "mobility_status"
            entry["status"] = sentence
            results.append(entry)
            continue

    return results

# -----------------------------
# Test locally
# -----------------------------
if __name__ == "__main__":
    sample = """
    Knee flexion improved from 30 to 45 degrees today.
    External rotation is still limited, around 20 degrees.
    Swelling around knee is 2 cm.
    Pain is 4/10.
    Some redness and pus observed.
    Patient can walk with slight limp.
    Shoulder abduction is about 80 degrees.
    """

    import json
    print(json.dumps(extract_rom_data(sample), indent=4))
