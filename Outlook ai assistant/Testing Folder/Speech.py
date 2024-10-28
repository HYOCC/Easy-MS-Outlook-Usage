import speech_recognition as sr


recognizer = sr.Recognizer()


def record_audio(): #Audio recorder 
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    return audio


def recognize_speech(audio): #proccesses the audio data into texts
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand that.")
    except sr.RequestError:
        print("Sorry, there was an error processing your request.")

if __name__ == "__main__":
    while True:
        audio = record_audio()
        recognize_speech(audio)

