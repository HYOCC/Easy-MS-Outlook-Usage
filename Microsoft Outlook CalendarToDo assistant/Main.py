from openai import OpenAI
import webview
import threading
from flask import Flask, render_template, request, jsonify
from asyncio import run as runs
from datetime import datetime, date
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from dotenv import load_dotenv

import Get_Data.Auth.Microsoft_authy as Authy 
from Get_Data.Calendar import create_event, delete_event, get_events, create_categories, Create_event_with_recurrence, get_categories, update_event_with_recurrence, update_event, delete_categories, get_recurring_event_id, get_single_event_id
from Get_Data.mic_function import user_voice
from Get_Data.Tasklist import create_tasklist, get_tasklist, update_tasklist, delete_tasklist 
from Get_Data.Tasklist_todo import get_task_in_tasklist, create_task_in_tasklist, update_task_in_tasklist

#The tools the AI have access to
Calendar_tool = [create_event, delete_event, get_events, create_categories, Create_event_with_recurrence, get_categories, update_event_with_recurrence, update_event, delete_categories, get_recurring_event_id, get_single_event_id]
Tasklist_tool = [create_tasklist, get_tasklist, update_tasklist, delete_tasklist]
Tasklist_todo_tool = [get_task_in_tasklist, create_task_in_tasklist, update_task_in_tasklist]


#Starts flask application which allows integration of html data to python data and vice versa
app = Flask(__name__)

#Sets up the configuration for GenAI Google
default_ai_content = f'''
You are a calendar/TO DO task assistant that can access external functions. You also act like a butler for talking needs. The user might try and use voice so please respond accordingly. You are talking to the user directly through voice. Your name is Gill.
Current date is {date.today()}, {date.today().strftime("%A")}

General Rule: 
1. Use military time (01:00:00 to 23:59:59) for system only
2. Call only the necessary function based on the latest user message.
3. Ask for clarification if user intent is unclear or if not enough information is received
4. Talk to the user since you are speaking to them using voice. So talk like human
5. Convert all time to AM/PM
6. Assume always use date that is not in the past
7. Associate Calendar with events, meeting etc
8. Associate Tasklist with things that has a due date or a to do item such as homeworks chores etc.
9. You must call get_tasklist first before calling create_task_in_tasklist

- Use function such as get_recurring_event_id, get_single_event_id, get_task_in_tasklist, get_tasklist to get the id necessary to make changes or deleting an item. If you cant find an item, try using the other related function first before asking futher to the users


'''
Safety_rating = {   
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
}

#Loads the api_key from a secure file called APIKey.env and sets up the google AI configs
load_dotenv('APIKey.env')
genai.configure(api_key=os.getenv('google_api_key'))
tool_config = {
  "function_calling_config": {
    "mode": "AUTO",
  }
}

global_events = ''
categories = ''

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
    return render_template('gerald.html')
#When user sends a text
@app.route('/user_input', methods=['POST'])
def user_input():
    global chat
    user_content = request.form.get('user_input')
    if user_content:
        #Gets the currently existing event and category and feeds it to the bot
        dt = datetime.now().strftime("%I:%M%p") 
        #The message that is sent to the bot 
        response  = chat.send_message(f'Current time is: {dt}\n' + user_content)
        
        return render_template('chatbox.html', ai_response = response.text)
    return render_template('chatbox.html')

@app.route('/voice', methods=['POST'])
def voice():
    user_voice() 
    
@app.route('/gerald', methods=['POST'])
def gerald_voice():
    global chat
    data = request.get_json()['action']

    
    if data:
        #Gets the currently existing event and category and feeds it to the bot
        dt = datetime.now().strftime("%I:%M%p") 
        #The message that is sent to the bot 
        response  = chat.send_message(f'Current time is: {dt}\n' + data)
        
        
        return jsonify({'ai_message': response.text})
        
        return render_template('gerald.html', ai_response = response.text)
    return render_template('gerald.html')
    


async def run():
    global global_events, default_ai_content, chat
    
    await Authy.run_data() #Starts the authentication for microsoft account and gets the authorization key set up

    #Sets up the initialization of the AI
    model = genai.GenerativeModel('gemini-1.5-pro', safety_settings= Safety_rating, tools=Calendar_tool + Tasklist_tool + Tasklist_todo_tool,tool_config=tool_config,system_instruction=default_ai_content)
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    #Lets the website run in the background and starts it
    app_thread = threading.Thread(target=web_start)
    app_thread.start()
    
    #Creates the window of the website and presents 
    create_webview()

if __name__ == "__main__":
    runs(run())
    
