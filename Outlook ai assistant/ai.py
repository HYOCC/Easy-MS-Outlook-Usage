from openai import OpenAI 
import webview 
import threading 
from flask import Flask, render_template, request 
import asyncio
from get_data import run_data, create_event 
from bs4 import BeautifulSoup
from datetime import datetime
import json 

app = Flask(__name__)
client = OpenAI(
    base_url = "https://api.together.xyz/v1",
    api_key = 'API-key goes here',
)
default_ai_content = '''
You are a calendar assistant AI that can access external functions. 

When a user requests to ONLY View events:
1. Format the event information into a readable HTML structure.
2. Present each upcoming event on a new line within the HTML.
3. Use appropriate HTML tags to enhance readability and structure.
4. Include only the HTML code in your response, without explanations.
5. Put the time in AM/PM format with the date.
6. Greet and present the information like a personal assistant/butler.
7. Make the interface look user presentable
8. if the user specifies a specific date, only give the information from the requested date and the date is no longer required be printed
9. If there is no events for the specified time, just say No events in a good manner 
ex. User will ask for 'Whats my event for today? what do i have for plans for today?' 

When a user is requesting to add new events:
1. Use the supplied functions to create the event. 
ex. the user will ask such as 'create an event' or 'add an event', these examples are not the only way, be flexible about it.

if you dont know what the user is asking for, ask the user to reconfirm whether they are trying to create an event or view an event.
'''
already_exsiting_events = []

def web_start(): 
    app.run(debug=True, use_reloader=False) 


def create_webview():
    webview.create_window("Home", "http://127.0.0.1:5000/", maximized=True)
    webview.start()

@app.route('/')
def home():
    return render_template('chatbox.html')

@app.route('/user_input', methods=['POST'])
def user_input():
    user_content = request.form.get('user_input')
    if user_content: 
        user_content += f'Already existed events: {already_exsiting_events}'
        message = [
        {'role': 'system', 'content': default_ai_content},
        {'role': 'user', 'content': f'Today\'s date is: {datetime.now()} for reference, {user_content}' }
        ]
        tools = [
            {
                'type': 'function',
                'function': {
                    'name':'create_event',
                    'description': 'create the event(s) in the outlook calendar. Call this whenever the user requests an events to be added/created',
                    'parameters':{
                        'type': 'object',
                        'properties':{
                            'event_name':{
                                'type': 'string',
                                'description': 'The event\'s name' 
                            },
                            'start_date':{
                                'type': 'string',
                                'description': 'The event\'s start date in year-month-date format'
                            },
                            'end_date':{
                                'type': 'string',
                                'description': 'The event\'s end date in year-month-date format' 
                            },
                            'start_time':{
                                'type': 'string',
                                'description': 'The event\'s start time in hr:min:sec format' 
                            },
                            'end_time':{
                                'type': 'string',
                                'description': 'The event\'s end time in hr:min:sec format' 
                            },
                            'location_name':{
                                'type': 'string',
                                'description': 'The event\'s name' 
                            },
                            'categories':{
                                'type': 'string',
                                'description': 'The event\'s category, such as School events, club events etc. The user will specify by saying such as \'its a school event\' category being school or \'event under schools\' category being schools or by saying category before the categories\'s name. DONT include the category with it' 
                            },
                            'recurrence':{
                                'type': 'boolean',
                                'description': 'True if the User requests the event to be repeated, false otherwise'
                            },
                            'reccurence_pattern':{
                                'type': 'string',
                                'description': 'Value is set to \'weekly\' if user wants event to repeat every week, \'daily\' if user wants the event to be repeated day by day'  
                            },
                            'reccurence_range': {
                                'type': 'tuple',
                                'description': 'Value is set (start_date, end_date) for the tuples' 
                            },
                            'reccurence_week':{
                                'type': 'string',
                                'description': 'The day of the week that the user wants the event to be repeated over. Always include the value to all valid weekdays and also lowercase such as \'monday\''
                            }
                        },
                        'required': ['event_name', 'start_date','end_date','start_time','end_time']
                    }
                }
            }
        ]
        
        data = client.chat.completions.create(model = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", messages=message, tools=tools, tool_choice='auto')
        response = data.choices[0].message.content
        if data.choices[0].message.tool_calls:
            tool_call = data.choices[0].message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            event_name = arguments.get('event_name')
            start_date=arguments.get('start_date')
            end_date=arguments.get('end_date')
            start_time=arguments.get('start_time')
            end_time=arguments.get('end_time')
            if arguments.get('location_name'):
                location = arguments.get('location_name')
            else:
                location = None
            if arguments.get('categories'):
                categories = arguments.get('categories')
            else:
                categories = None
            if arguments.get('recurrence'):
                reccurence = arguments.get('recurrence')
                print(reccurence)
        
            already_exsiting_events.append(f'new events: {event_name}, {start_date}, {end_date}, {start_time}, {end_time}, {location}, {categories}')
            message.append({'role':'system', 'content': response})
            message.append({'role':'user', 'content': user_content})
            create_event(event_name, start_date, end_date, start_time, end_time, location, categories)
            return render_template('chatbox.html', ai_response = 'success')
        message.append({'role':'system', 'content': response})
        message.append({'role':'user', 'content': user_content})
        return render_template('chatbox.html', ai_response = response)
    return render_template('chatbox.html') 


async def run():
    global already_exsiting_events 
    already_exsiting_events.append(await run_data())
    app_thread = threading.Thread(target=web_start)
    app_thread.start()
    create_webview() 
    
if __name__ == "__main__":
    asyncio.run(run())


