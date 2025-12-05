import speech_recognition as sr

def transcribe_voice():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        return text
    except:
        return ""
