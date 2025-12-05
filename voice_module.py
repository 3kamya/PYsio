import speech_recognition as sr
from pydub import AudioSegment

# ---------------------------
# Transcribe microphone input
# ---------------------------
def transcribe_microphone():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return ""

# ---------------------------
# Transcribe uploaded audio file
# ---------------------------
def transcribe_uploaded_file(uploaded_file):
    # Convert to WAV if needed
    audio = AudioSegment.from_file(uploaded_file)
    audio.export("temp.wav", format="wav")
    
    r = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = r.record(source)
    try:
        return r.recognize_google(audio_data)
    except:
        return ""
