import re

# -----------------------------
# ROM keywords your system can understand
# Add or modify as needed
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


# -----------------------------
# Helper function — find which ROM term is present in the sentence
# -----------------------------
def detect_rom_type(text):
    text = text.lower()
    for keyword in ROM_KEYWORDS:
        if keyword in text:
            return ROM_KEYWORDS[keyword], keyword
    return None, None


# -----------------------------
# Main extraction function
# -----------------------------
def extract_rom_data(transcript):
    transcript = transcript.lower()

    results = []

    # Split transcript into sentences for easier parsing
    sentences = re.split(r'[.,;]', transcript)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        #  Find ROM type in the sentence
        rom_code, rom_phrase = detect_rom_type(sentence)
        if not rom_code:
            continue

        #  Pattern: "from X to Y degrees"
        match_range = re.search(r'from\s+(\d+)\s+to\s+(\d+)\s*degrees?', sentence)
        if match_range:
            start_val = int(match_range.group(1))
            end_val = int(match_range.group(2))
            results.append({
                "rom_type": rom_code,
                "rom_phrase": rom_phrase,
                "start": start_val,
                "end": end_val
            })
            continue

        #  Pattern: "around X degrees"
        match_around = re.search(r'around\s+(\d+)\s*degrees?', sentence)
        if match_around:
            val = int(match_around.group(1))
            results.append({
                "rom_type": rom_code,
                "rom_phrase": rom_phrase,
                "start": None,
                "end": val
            })
            continue

        # Pattern: "improved / increased / reduced ... X degrees"
        match_improve = re.search(
            r"(improved|increased|reduced).*?(\d+)\s*degrees?",
            sentence
        )
        if match_improve:
            val = int(match_improve.group(2))
            results.append({
                "rom_type": rom_code,
                "rom_phrase": rom_phrase,
                "start": None,
                "end": val
            })
            continue

        # Simple pattern: "X degrees"
        match_single = re.search(r'(\d+)\s*degrees?', sentence)
        if match_single:
            val = int(match_single.group(1))
            results.append({
                "rom_type": rom_code,
                "rom_phrase": rom_phrase,
                "start": None,
                "end": val
            })
            continue

    return results


# -----------------------------
# Test locally
# -----------------------------
if __name__ == "__main__":
    sample = """
    Knee flexion improved from 30 to 45 degrees today.
    External rotation is still limited, around 20 degrees.
    Shoulder abduction is about 80 degrees.
    """

    print(extract_rom_data(sample))
