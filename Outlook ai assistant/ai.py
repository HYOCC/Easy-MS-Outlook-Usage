from openai import OpenAI
import webview
import threading
from flask import Flask, render_template, request, jsonify
from asyncio import run as runs
from get_data import run_data, create_event, delete_event, get_events, Create_event_with_recurrence, get_categories
from datetime import datetime
import speech_recognition as sr
import google.generativeai as genai
import os
from dotenv import load_dotenv

#Starts flask application which allows integration of html data to python data and vice versa
app = Flask(__name__)

#Sets up the configuration for GenAI Google
default_ai_content = '''
You are a calendar assistant AI that can access external functions. You also act like a butler for talking needs. The user might try and use voice so please respond accordingly 

General: 
1. Use military time (01:00:00 to 23:59:59) for system only
2. Call only the necessary function based on the latest user message.
3. Ask for clarification if user intent is unclear.
4. Format output in readable HTML
5. You can use more than one function
6. CASE sensitive for functions. Dont uppercase the parameters except if told to do so

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
-If user wants all of their event, go from current time and date to next year

Creating events: 
-Use create_event function if user doesnt want the event to repeat. Use Create_event_with_recurrence if the user wants the event to repeat. 
-Respond to various phrasings (e.g., "create an event", "add an event")
-NEED specified time


Deleting events:
-get the event ID from a list of event that is given to you and always use the latest added one, the message starts with \'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\' and use delete_event function
-If the user asks to remove a event that occurs every specific day, just get the id of the that event that pops up first and use that.
-Require event name from user
-If event doesn't exist, inform user before proceeding to delete the closest one named after it.
-If event name is not provided, ask for clarification
-Don't select events randomly
-Response format:
-For viewing: HTML only, no explanations
'''
#Loads the api_key from a secure file caclled APIKey.env and sets up the google AI configs
load_dotenv('APIKey.env')
genai.configure(api_key=os.getenv('google_api_key'))
tool_config = {
  "function_calling_config": {
    "mode": "AUTO",
  }
}


global_events = ''

#Sets up the speech to text model
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.5
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



 #To be deleted

#To be deleted
tools = [
            {
                'type': 'function',
                'function': {
                    'name': 'create_event',
                    'description': 'Create the event(s) in the Outlook calendar. Call this whenever the user requests an event to be added/created',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'event_name': {'type': 'string', 'description': 'The event\'s name'},
                            'start_date': {'type': 'string', 'description': 'The event\'s start date in year-month-date format'},
                            'end_date': {'type': 'string', 'description': 'The event\'s end date in year-month-date format'},
                            'start_time': {'type': 'string', 'description': 'The event\'s start time in hr:min:sec format'},
                            'end_time': {'type': 'string', 'description': 'The event\'s end time in hr:min:sec format'},
                            'location_name': {'type': 'string', 'description': 'The event\'s location'},
                            'categories': {'type': 'string', 'description': f'The event\'s category, look for existing category first if there is no existing category, tell the user to specify which further'},
                            'notes': {'type':'string', 'description': 'The event\'s description such as if user wants to add a little info regarding the event.'}
                        },
                        'required': ['event_name', 'start_date', 'end_date', 'start_time', 'end_time']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'delete_event',
                    'description': 'Deletes an event by using the \'Event ID\' or \'event recurring ID\'',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'description': 'The event id or event recurring ID'},
                        },
                        'required': ['id']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_events',
                    'description': 'Gets all the events in the specified time frame',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'start_date_time': {'type': 'string', 'description': 'The user specified starting time in the format of year-month-dayTmilitaryHour:minutes:seconds'},
                            'end_date_time': {'type': 'string', 'description': 'The user specified end time frame in the format of year-month-dayTmilitaryHour:minutes:seconds'}
                        },
                        'required': ['start_date_time', 'end_date_time']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'Create_event_with_recurrence',
                    'description': 'Creates an event with the events reccuring either weekly or monthly',
                    'parameters':{
                        'type': 'object',
                        'properties': {
                            'event_name': {'type': 'string', 'description': 'The event\'s name'},
                            'start_date': {'type': 'string', 'description': 'The event\'s start date in year-month-date format'},
                            'end_date': {'type': 'string', 'description': 'The event\'s end date in year-month-date format.'},
                            'start_time': {'type': 'string', 'description': 'The event\'s start time in hr:min:sec format'},
                            'end_time': {'type': 'string', 'description': 'The event\'s end time in hr:min:sec format, No need if type is numbered'},
                            'range': {'type': 'list', 'description': 'The start date and end date of the recurring event, first index is always start_date and second index is end_date. If user doesnt specify a end date, only put first index start_date'},
                            'interval': {'type': 'integer', 'description': 'The number of units between occurrences, where units can be in days, weeks, months, or years, depending on the type parameter'},
                            'pattern_type': {'type':'string', 'enum':['daily', 'weekly', 'absoluteMonthly', 'absoluteYearly'], 'description': 'The type of reccurence the user wants'},
                            'end_type': {'type':'string', 'enum':['endDate', 'noEnd', 'numbered'], 'description': f'**IF the user wants to create event on multiple days in a week just for one week, use numbered and set numberofoccurrence to 1. If user has a date in mind which the recurrence should end, use endDate. Else if the user wants it to repeat a certain time, user numbered. Else if the user doesnt specify a date use noEnd.'},
                            'daysOfWeek': {'type':'list', 'enum':['monday','tuesday','wednesday','thursday','friday','saturday','sunday'], 'description': 'The day of the week that the user wants the event to be repeated on if the type parameter is weekly, if none are specified, assume the day is the current day. It can be multiple days, format it into [], ex. [\'monday\', \'tuestday\'], [\'monday\']'},
                            'dayOfMonth': {'type':'integer', 'description': 'The day of the month that the user wants the event to be repeated on, if none are specified, assume its the current date'},
                            'location_name': {'type': 'string', 'description': 'The event\'s location'},
                            'categories': {'type': 'string', 'description': 'The event\'s category, such as School events, club events etc.'},
                            'notes': {'type':'string', 'description': 'The event\'s description such as if user wants to add a little info regarding the event.'},
                            'numberOfOccurrences': {'type': 'integer', 'description': 'If end_type is numbered, this is the number of times that the set of event repeat for.'}
                        },
                        'required': ['event_name', 'start_date', 'start_time', 'end_date', 'end_time', 'range', 'pattern_type', 'end_type']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_categories',
                    'description': 'Gets all of the existing categories information such as name, color and id',
                    'parameters':{
                        'type': 'object',
                        'properties': {},
                        'required': [] 
                    }
                }
            }
        ]


def web_start():
    app.run()

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
    global global_events, chat, default_ai_content
    user_content = request.form.get('user_input')
    if user_content:
        #Gets the currently existing event and category and feeds it to the bot
        dt = datetime.now() 
        global_events = get_events(None, None) 
        categories = get_categories()
        default_ai_content += f'DONT READ BELOW unless trying to get the existing categories that the user has\n {categories}\n' + f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}\n'
        model = genai.GenerativeModel("gemini-1.5-pro", tools=[get_events, create_event, delete_event, Create_event_with_recurrence, get_categories],tool_config=tool_config,system_instruction=default_ai_content)
        chat = model.start_chat(enable_automatic_function_calling=True)
        #The message that is sent to the bot 
        response = chat.send_message(f'Today\'s date and time is: {dt} for reference (For AI to read), week of day is {dt.strftime('%A')}\n' + user_content) 
        
        return render_template('chatbox.html', ai_response = response.text)
    return render_template('chatbox.html')


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
    

async def run():
    global global_events, default_ai_content, chat 
    await run_data() #Starts the authentication for microsoft account and gets the authorization key set up
    
    #Lets the website run in the background and starts it
    app_thread = threading.Thread(target=web_start)
    app_thread.start()
    
    #Creates the window of the website and presents 
    create_webview()

if __name__ == "__main__":
    runs(run())
    
