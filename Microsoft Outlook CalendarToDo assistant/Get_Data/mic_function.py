import speech_recognition as sr
from requests import request
from flask import request, jsonify

#Sets up the speech to text model
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.5



#Transfer to another file better readability
mic = False
audio_data = None 

def user_voice():
    global mic, audio_data
    
    if request.json['action'] == 'button_clicked':
        mic = True 
    
    if mic:
        print('mic on')
        while mic: #Toggle on mic to get raw audio data
            audio_data = listen_audio()
            mic = False
    
    if not(mic) and audio_data:
        print('proccessing data')
        try: #When mic is turned off, the raw data is processed 
            text = recognizer.recognize_google(audio_data)
            print(f"You said: {text}")
        except:
            print('error')
            return jsonify({'response': 'AI instruction: say \'please repeat what you said \''})
        
        audio_data = None 
        return jsonify({'response': text})
    
    return jsonify({'response': ''})


def listen_audio():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    return audio
