from openai import OpenAI
import webview
import threading
from flask import Flask, render_template, request, jsonify
from asyncio import run as runs
from get_data import run_data, create_event, delete_event, get_events, Create_event_with_recurrence, get_categories
from datetime import datetime
from json import loads, dumps
import speech_recognition as sr

app = Flask(__name__)
client = OpenAI(
    base_url="https://api.together.xyz/v1",
    api_key='dd3959d6ed9e934c0eb3264586456495f25d9ce07426af34ac98fcd049c24043'
)

recognizer = sr.Recognizer()

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

global_events = ''

default_ai_content = '''
You are a calendar assistant AI that can access external functions. 

General: 
1. Use military time (01:00:00 to 23:59:59).
2. Call only the necessary function based on the latest user message.
3. Ask for clarification if user intent is unclear.
4. Format output in readable HTML with white text and in fun font, dont change background color
5. You can use more than one function


Viewing events:
-Use get_events function
-Format in readable HTML, each event should be its own line, put it into table/column for better readability
-Use AM/PM format with date
-Present as a personal assistant/butler
-For specific dates, omit date in output
-If no events, respond creatively
-Omit event ID and seriesmasterID 
-For upcoming events, show from current date/time to the next 
-For repeating events, only show the next upcoming event. repeating events are as specified, same time and same day of the week. ex. both are monday and 2pm to 5pm, put the next upcooming one only
-If the starting date/time is not specificed, ALWAYS go from the current date time 
-Include what day of the week it is

Adding events:
-Use create_event function if user doesnt want the event to repeat. Use Create_event_with_recurrence if the user wants the event to repeat. 
-Respond to various phrasings (e.g., "create an event", "add an event")
-NEED specified time



DONT read below unless trying to delete the event
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

message = [{'role': 'system', 'content': default_ai_content}, {'role': 'system', 'content': f'Today\'s date and time is: {datetime.now()} for reference (For AI to read)'}]

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
                            'range': {'type': 'list', 'description': 'The start date and end date of the recurring event,[start_date, end_date]. If user doesnt specify a end date, only put the start_date and leave end_date empty, [start_date]'},
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

@app.route('/')
def home():
    return render_template('chatbox.html')

@app.route('/user_input', methods=['POST'])
def user_input():
    global global_events
    user_content = request.form.get('user_input')
    if user_content:
        message.append({'role':'user', 'content': f'{user_content}'})
        data = client.chat.completions.create(model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", messages=message, tools=tools, tool_choice='auto')
        if data.choices[0].message.tool_calls:            
            for tool_call in data.choices[0].message.tool_calls:
                arguments = loads(tool_call.function.arguments)
                if tool_call.function.name == 'get_events':
                    events = get_events(arguments.get('start_date_time'), arguments.get('end_date_time'))
                    message.append({"tool_call_id": tool_call.id, "role": "tool", "name": tool_call.function.name, "content": dumps(events)})
                    data = client.chat.completions.create(model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", messages=message)
                    response = data.choices[0].message.content
                    return render_template('chatbox.html', ai_response=response)
                elif tool_call.function.name == 'create_event':
                    response_code, response = create_event(
                        arguments.get('event_name'),
                        arguments.get('start_date'),
                        arguments.get('end_date'),
                        arguments.get('start_time'),
                        arguments.get('end_time'),
                        arguments.get('location_name'),
                        arguments.get('categories')
                    )
                    response = response.json() 
                    global_events += f"Event: Title = {response['subject']}, Time = {response['start']['dateTime']} - {response['end']['dateTime']}, Location = {response['location']['displayName']}, Event ID = {response['id']}\n"
                    message[2] = {'role': 'system', 'content': f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}'}
                    
                    message.append({"tool_call_id": tool_call.id, "role": "tool", "name": tool_call.function.name, "content": dumps(response_code)})
                    
                    return render_template('chatbox.html', ai_response=response_code)
                elif tool_call.function.name == 'delete_event':
                    response_code = delete_event(arguments.get('id'))
                    print(arguments.get('id'))
                    message.append({"tool_call_id": tool_call.id, "role": "tool", "name": tool_call.function.name, "content": dumps(response_code)})
                    return render_template('chatbox.html', ai_response=response_code)
                elif tool_call.function.name == 'Create_event_with_recurrence':
                    response_code = Create_event_with_recurrence(
                    arguments.get('event_name'),
                    arguments.get('start_date'),
                    arguments.get('end_date'),
                    arguments.get('start_time'),
                    arguments.get('end_time'),
                    arguments.get('range'),
                    arguments.get('interval'),
                    arguments.get('pattern_type'),
                    arguments.get('end_type'),
                    arguments.get('location_name'),
                    arguments.get('categories'),
                    arguments.get('daysOfWeek'),
                    arguments.get('dayOfMonth'),
                    arguments.get('numberOfOccurrences')                      
                    )
                    global_events += f"Event: Title = {response['subject']}, Time = {response['start']['dateTime']} - {response['end']['dateTime']}, Location = {response['location']['displayName']}, Event ID = {response['id']}\n"
                    message[2] = {'role': 'system', 'content': f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}'}
                    
                    message.append({"tool_call_id": tool_call.id, "role": "tool", "name": tool_call.function.name, "content": dumps(response_code)})
                    return render_template('chatbox.html', ai_response = response_code)
                elif tool_call.function.name == 'get_categories':
                    categories = get_categories() 
                    message[3] = {'role': 'system', 'content': f'DONT READ BELOW unless trying to get the existing categories that the user has\n {categories}'}
        data = client.chat.completions.create(model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", messages=message)
        response = data.choices[0].message.content
        return render_template('chatbox.html', ai_response=response)
    return render_template('chatbox.html')

@app.route('/voice',  methods=['POST'])
def user_voice():
    mic = False 
    if request.json['action'] == 'button_clicked':
        mic = not(mic) 

    while mic:
        text = ''
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
        except sr.RequestError:
            print("Sorry, there was an error processing your request.")
        if not(text):
            continue 
        mic = False 
    return jsonify({'response': text})
    
        



async def run():
    global global_events
    await run_data()
    global_events = get_events() 
    message.append({'role': 'system', 'content': f'DONT READ BELOW UNLESS TRYING TO DELETE EVENTS\n {global_events}'})
    categories = get_categories()
    message.append({'role': 'system', 'content':f'DONT READ BELOW unless trying to get the existing categories that the user has\n {categories}'})
    app_thread = threading.Thread(target=web_start)
    app_thread.start()
    create_webview()

if __name__ == "__main__":
    runs(run())
    
