
import google.generativeai as genai
from datetime import datetime

genai.configure(api_key='AIzaSyCTjG0mDHd0GYgjCfMVB6qWFRtSEwgYAxg')


#Default testing, function testing 
def enable_lights(bot_name:str):
    """Turn on the lighting system.
    
    Args:
    bot_name: The bots name 
    
    
    """

    return bot_name + ': Lights enabled.'
def change_light(color:str):
  """
  Changes the light color
  """
  
  return 'Color changed'

tool_config = {
  "function_calling_config": {
    "mode": "AUTO",
  }
}


model = genai.GenerativeModel("gemini-1.5-pro", tools=[enable_lights, change_light],tool_config=tool_config,system_instruction='You are a helpful lighting system bot. You can turn lights on and off, and you can set the color. Do not perform any other tasks. Ask for clarification if parameters are not met')
chat = model.start_chat(enable_automatic_function_calling=False)


response = chat.send_message('hi, whats your name')
print(response.candidates[0].content.parts)

if response.candidates[0].content.parts[0].function_call:
    print('true')
for functions in response.candidates[0].content.parts:
    print(functions.function_call.name)
    
#chat = model.start_chat(enable_automatic_function_calling=True)
#response = chat.send_message('turn on the light for OscarBot and change the color to red')
#print(response.text)


'''
#Chatbot records history of the chat down 
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(
    history=[
        {"role": "user", "parts": "Hello"},
        {"role": "model", "parts": "Great to meet you. What would you like to know?"},
    ]
)
response = chat.send_message("I have 2 dogs in my house.")
print(response.text)
response = chat.send_message("How many paws are in my house?")
print(response.text)
response = chat.send_message("how much dogs do i have again?")
print(response.text)

#Implementation on how to get the response in chunks rather than waiting for the whole text to be finished, using chunk
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(
    history=[
        {"role": "user", "parts": "Hello"},
        {"role": "model", "parts": "Great to meet you. What would you like to know?"},
    ]
)
response = chat.send_message("I have 2 dogs in my house.", stream=True)
for chunk in response:
    print(chunk.text)
    print("_" * 80)
response = chat.send_message("How many paws are in my house?", stream=True)
for chunk in response:
    print(chunk.text)
    print("_" * 80)

print(chat.history)

#Configuration of the model
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(
    "Tell me a story about a magic backpack.",
    generation_config=genai.types.GenerationConfig(
        # Only one candidate for now.
        candidate_count=1, #How much response the ai will be given, defaults to 1 
        stop_sequences=["x"], # specifies the set of character sequences (up to 5) that will stop output generation
        max_output_tokens=20, #Maximum number of token in ONE candidate 
        temperature=1.0, #controls the randomness higher for more creative and lower for more stable repsonse range from [0.0,2.0]
    ),
)

print(response.text)

'''


"""
#Changing the danger settingn 
from google.generativeai.types import HarmCategory, HarmBlockThreshold

#TESTING dictionary with ai - WORKS 
dict = {
    'OpenLight': 'code1',
    'CloseLight': 'code2'
}

def updating_light(code:str):
    '''
    Updates the light
    
    ARGS:
    code: The string that the user want
    '''
    if code == 'code1':
        print('OPENLIGHT BOMBA')
        return 'success'

    if code == 'code2':
        print('CloseLight')
        return 'success'
    
    return 'non_sucess'

model = genai.GenerativeModel("gemini-1.5-pro", tools=[updating_light] ,safety_settings={HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE}, system_instruction=f'{dict}\n If the user wants to open the light, from the dictionary get the value from it. Same thing for closing the light')
chat = model.start_chat(enable_automatic_function_calling=True)

response = chat.send_message('Hi, open the light')
print(response.text)
"""

'''
for model_info in genai.list_tuned_models():
    print(model_info.name)
else:
    print('printing model info for fine tuning')
'''