import webview
import threading
from flask import Flask, render_template, request, jsonify
from asyncio import run as runs
from datetime import datetime, date
import speech_recognition as sr
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold, content_types
import os
from dotenv import load_dotenv

import Get_Data.Auth.Microsoft_authy as Authy 
from Get_Data.Calendar import create_event, delete_event, get_events, create_categories, Create_event_with_recurrence, get_categories, update_event_with_recurrence, update_event, delete_categories
from Get_Data.function_setup import name 

#The tools the AI have access to
Calendar_tool = [create_event, delete_event, get_events, create_categories, Create_event_with_recurrence, get_categories, update_event_with_recurrence, update_event, delete_categories]

#Starts flask application which allows integration of html data to python data and vice versa
app = Flask(__name__)

#Sets up the configuration for GenAI Google
default_ai_content = f'''
You are a calendar assistant AI that can access external functions. You also act like a butler for talking needs. The user might try and use voice so please respond accordingly 
The text you are sending is placed inside  a <p> </p> format in html, so format your response correctly after you get your data from the function
Current date is {date.today()}, {date.today().strftime("%A")}

General Rule: 
1. Use military time (01:00:00 to 23:59:59) for system only
2. Call only the necessary function based on the latest user message.
3. Ask for clarification if user intent is unclear.
4. Default to only calling function once unless user's instruction calls for multiple function calls
5. Respond in AM/PM for user\n\n

function calling rule:
-use get_events() for getting the events for a specified time
-use create_event() or Create_event_with_recurrence() for creating event 
-use delete_event() or delete_categories() for deleting events/categories and use the event ids that was given to you below
-use create_categories() for creating categories for the event 
-use update_event_with_recurrence, update_event to update existing events 
'''
Safety_rating = {   
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
}

#Loads the api_key from a secure file caclled APIKey.env and sets up the google AI configs
load_dotenv('APIKey.env')
genai.configure(api_key=os.getenv('google_api_key'))
tool_config = {
  "function_calling_config": {
    "mode": "AUTO",
  }
}

global_events = ''
categories = ''
'''
#Sets up the speech to text model
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.5
'''

#Starts the application for Flask
def web_start():
    app.run()

#Creates the window
def create_webview():
    webview.create_window("Home", "http://127.0.0.1:5000/", fullscreen=True)
    webview.start()
    
#Initial Website
@app.route('/')
def home():
    return render_template('chatbox.html')



#When user sends a text
@app.route('/user_input', methods=['POST'])
def user_input():
    global global_events, chat, default_ai_content, categories, ai_content, model
    user_content = request.form.get('user_input')
    if user_content:
        #Current date and time 
        dt = datetime.now().strftime("%I:%M%p")
        user_content = f'Time is: {dt}\n' + user_content +'\n\n'
        
        #Sets auto function calling to false
        chat.enable_automatic_function_calling=False
        
        #Only updates the system if the Category or event changes 
        new_category =  get_categories()
        new_event = get_events(None,None)
        if categories != new_category or global_events != new_event:
            if categories != get_categories():
                print('category Changed')
                categories = new_category
            else:
                print('global events changed')
                global_events = new_event
            ai_content = default_ai_content + f'DONT READ BELOW unless trying to get the existing categories that the user has\n {categories}\n\n' + f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}\n\n'
            model = genai.GenerativeModel("gemini-1.5-pro", safety_settings= Safety_rating, tools=Calendar_tool,tool_config=tool_config,system_instruction=ai_content)
        
        #The message that is sent to the bot 
        response = chat.send_message(user_content) 
        
        #Gets each called function and updates the user content for further system instruction base on need basis  
        for functions in response.candidates[0].content.parts:
            function_calling = False #Determines whether a function was called or not
    
            if functions.function_call: #If there was a function that the AI decides to be caleld 
                #Logging
                print('Code 444')
                
                #A function was called
                function_calling = True
                user_content = name(functions.function_call.name) + user_content
                
        #enables auto function calling for the new model with new instruction and send the user message again 
        if function_calling: 
            chat.enable_automatic_function_calling = True 
            response = chat.send_message(user_content)
    
        try: 
            return render_template('chatbox.html', ai_response = response.text)
        except:
            print('error')
            return render_template('chatbox.html', ai_response = response)
        
        
    return render_template('chatbox.html')

#Transfer to another file better readability
'''
mic = False
audio_data = None 
@app.route('/voice',  methods=['POST'])
async def user_voice():
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
'''

async def run():
    global global_events, default_ai_content, chat, categories, ai_content, model
    
    await Authy.run_data() #Starts the authentication for microsoft account and gets the authorization key set up
    
    #Sets up the initialization of the AI
    global_events = get_events(None, None)
    categories = get_categories() 
    ai_content = default_ai_content + f'DONT READ BELOW unless trying to get the existing categories that the user has\n {categories}\n\n' + f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}\n\n'
    model = genai.GenerativeModel("gemini-1.5-pro",safety_settings= Safety_rating, tools=Calendar_tool,tool_config=tool_config,system_instruction=ai_content)
    chat = model.start_chat()
    
    #logging
    print(ai_content)
    
    #Lets the website run in the background and starts it
    app_thread = threading.Thread(target=web_start)
    app_thread.start()
    
    #Creates the window of the website and presents 
    create_webview()

if __name__ == "__main__":
    runs(run())
    
