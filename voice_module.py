import speech_recognition as sr
from pydub import AudioSegment
import os # <-- Needed for file cleanup
import traceback # <-- Needed to log full error messages

# ---------------------------
# Transcribe microphone input (FIXED)
# ---------------------------
def transcribe_microphone():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        # Use a timeout to prevent indefinite hanging if no audio is detected
        try:
            audio = r.listen(source, timeout=15, phrase_time_limit=25)
        except sr.WaitTimeoutError:
            print("No speech detected within the time limit.")
            return ""

    try:
        # Use language parameter for better accuracy if needed
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        # This occurs if you have an internet/API issue
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred during transcription: {e}")
        traceback.print_exc()
        return ""

# ---------------------------
# Transcribe uploaded audio file (FIXED & Safer)
# ---------------------------
def transcribe_uploaded_file(uploaded_file):
    temp_filename = "temp_audio_st.wav" 
    transcript = ""
    
    try:
        # 1. Convert to WAV (Requires FFmpeg)
        audio = AudioSegment.from_file(uploaded_file)
        audio.export(temp_filename, format="wav")
        
        # 2. Transcribe
        r = sr.Recognizer()
        with sr.AudioFile(temp_filename) as source:
            audio_data = r.record(source)
        
        transcript = r.recognize_google(audio_data)
        
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        transcript = ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        transcript = ""
    except Exception as e:
        # **This is where the FFmpeg error will appear!**
        print(f"FATAL ERROR (Check FFmpeg/pydub/audio file): {e}")
        traceback.print_exc()
        transcript = ""
        
    finally:
        # 3. CRITICAL: Clean up the temporary file regardless of success or failure
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
    return transcript
