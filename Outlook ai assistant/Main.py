from openai import OpenAI
import webview
import threading
from flask import Flask, render_template, request, jsonify
from asyncio import run as runs
from datetime import datetime
import speech_recognition as sr
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from dotenv import load_dotenv

import Get_Data.Auth.Microsoft_authy as Authy 
from Get_Data.Calendar import create_event, delete_event, get_events, create_categories, Create_event_with_recurrence, get_categories, update_event_with_recurrence, update_event 

#The tools the AI have access to
Calendar_tool = [create_event, delete_event, get_events, create_categories, Create_event_with_recurrence, get_categories, update_event_with_recurrence, update_event]

#Starts flask application which allows integration of html data to python data and vice versa
app = Flask(__name__)

#WIP for category functions
category_colors = {
    "Red": "Preset0",
    "Orange": "Preset1",
    "Brown": "Preset2",
    "Yellow": "Preset3",
    "Green": "Preset4",
    "Teal": "Preset5",
    "Olive": "Preset6",
    "Blue": "Preset7",
    "Purple": "Preset8",
    "Cranberry": "Preset9",
    "Steel": "Preset10",
    "DarkSteel": "Preset11",
    "Gray": "Preset12",
    "DarkGray": "Preset13",
    "Black": "Preset14",
    "DarkRed": "Preset15",
    "DarkOrange": "Preset16",
    "DarkBrown": "Preset17",
    "DarkYellow": "Preset18",
    "DarkGreen": "Preset19",
    "DarkTeal": "Preset20",
    "DarkOlive": "Preset21",
    "DarkBlue": "Preset22",
    "DarkPurple": "Preset23",
    "DarkCranberry": "Preset24"
}

#Sets up the configuration for GenAI Google
default_ai_content = f'''
You are a calendar assistant AI that can access external functions. You also act like a butler for talking needs. The user might try and use voice so please respond accordingly 

FOR ALL PURPOSE: 
1. Use military time (01:00:00 to 23:59:59) for system only
2. Call only the necessary function based on the latest user message.
3. Ask for clarification if user intent is unclear.
4. Format output in readable HTML format, make sure to clean the code well. For reference the html file already hase <p></p> and the html file set up already.
5. DONT have \'\'\'HTML in the beginning NOR \'\'\' IN THE END

Viewing events:
-Use get_events function
-each event should be its own line, put it into table/column for better readability. Order the events in chronological order
-convert military time to AM/PM format
-For specific dates, omit date in output
-If no events, respond creatively
-Omit event ID and seriesmasterID 
-If the starting date/time is not specificed, ALWAYS go from the current date time 
-Include what day of the week it is
-Only show events that has not occured yet (dates and time that are bigger than current date and time)
-Include location if applicable
-If user wants all of their event, go from current time and date to next month 
-If the user asks for next event, use get_events that goes from today, to tomorrow to the next day until there is a event.

Creating events: 
-Use create_event function if user doesnt want the event to repeat. Use Create_event_with_recurrence if the user wants the event to repeat. 
-Respond to various phrasings (e.g., "create an event", "add an event")
-NEED specified time
-If the user wants to assign the event to a unexisting category, ask the user for a color if not provided and use this dictionary {category_colors} that corresponds to the preset of the color. Create the category, then use get_categories and assign the event to the newly created category. If the color isnt in the dictionary, use the closest relating one

Updating existing event:
WIP 

Deleting events:
-get the event ID from a list of event that is given to you and always use the latest added one, the message starts with \'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\' and use delete_event function
-If the user asks to remove a event that occurs every specific day, just get the id of the that event that pops up first and use that.
-Require event name from user
-If event doesn't exist, inform user before proceeding to delete the closest one named after it.
-If event name is not provided, ask for clarification
-Don't select events randomly
-Response format:
-For viewing: HTML only, no explanations\n
\n
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
#Sets up the speech to text model
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.5

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
    global global_events, chat, default_ai_content, categories
    user_content = request.form.get('user_input')
    if user_content:
        #Gets the currently existing event and category and feeds it to the bot
        dt = datetime.now() 
        #Only updates the system if the event changes 
        if global_events != get_events(None,None):
            print('global events changed')
            default_ai_content += f'DONT READ BELOW unless trying to get the existing categories that the user has\n {categories}\n\n' + f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}\n\n'
            model = genai.GenerativeModel("gemini-1.5-pro", safety_settings= Safety_rating, tools=Calendar_tool,tool_config=tool_config,system_instruction=default_ai_content)
            chat = model.start_chat(enable_automatic_function_calling=True)
        #Only updates the system if the Category changes 
        if categories != get_categories():
            print('category Changed')
            default_ai_content += f'DONT READ BELOW unless trying to get the existing categories that the user has\n {categories}\n\n' + f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}\n\n'
            model = genai.GenerativeModel("gemini-1.5-pro", safety_settings= Safety_rating, tools=Calendar_tool,tool_config=tool_config,system_instruction=default_ai_content)
            chat = model.start_chat(enable_automatic_function_calling=True)
        #The message that is sent to the bot 
        response = chat.send_message(f'Today\'s date and time is: {dt} for reference (For AI to read), week of day is {dt.strftime('%A')}\n' + user_content) 
        
        return render_template('chatbox.html', ai_response = response.text)
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
    global global_events, default_ai_content, chat, categories 
    
    await Authy.run_data() #Starts the authentication for microsoft account and gets the authorization key set up
    
    #Sets up the initialization of the AI
    global_events = get_events(None, None)
    categories = get_categories() 
    default_ai_content += f'DONT READ BELOW unless trying to get the existing categories that the user has\n {categories}\n' + f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}\n'
    model = genai.GenerativeModel("gemini-1.5-pro", safety_settings= Safety_rating, tools=Calendar_tool,tool_config=tool_config,system_instruction=default_ai_content)
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    #Lets the website run in the background and starts it
    app_thread = threading.Thread(target=web_start)
    app_thread.start()
    
    #Creates the window of the website and presents 
    create_webview()

if __name__ == "__main__":
    runs(run())
    
