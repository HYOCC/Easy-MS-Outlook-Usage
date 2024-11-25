import speech_recognition as sr


recognizer = sr.Recognizer()
recognizer.energy_threshold = 4000
recognizer.dynamic_energy_threshold = True

def record_audio(): #Audio recorder 
    with sr.Microphone() as source:
        #recognizer.adjust_for_ambient_noise(source=source, duration = 1)
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

