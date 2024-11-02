import requests
from datetime import datetime, timedelta 
from configparser import SectionProxy
from azure.identity import  InteractiveBrowserCredential
from msgraph import GraphServiceClient
import configparser
from asyncio import run as runs
import Auth.Microsoft_authy as MA 

def create_tasklist(displayName:str):
    global headers
    '''
    Creates a todo category, for example a task lisk for life or homework etc 
    
    ARGS:
    displayname: The name of the category
    '''
    
    url = 'https://graph.microsoft.com/v1.0/me/todo/lists'
    request_body = {
        'displayName': displayName # The name of the task list
    }
    
    response = requests.post(url=url, headers=headers, json=request_body)
    
    if response.status_code == 201:
        print(f'Success in creating tasklist {displayName}')
        return 'success'
    else:
        print('not successful, please ask the user to retry or specify condition that is needed') 
        print(response.status_code)
        return 'not successful'

#Gets the info of the task lists
def get_tasklist(name:str):
    '''
    Gets the tasklist information using the name off the tasklist
    
    ARGS:
    name: the name of the tasklist 
    
    returns the id 
    '''
    url = 'https://graph.microsoft.com/v1.0/me/todo/lists'
    
    response = requests.get(url, headers=headers)
    
    tasklist = ''
    
    if response.status_code == 200:
        data = response.json()
        for item in data['value']:
            if item['displayName'].lower() == name.lower():
                tasklist += f'Tasklist Name: {item['displayName']}, Tasklist ID: {item['id']}\n'
                
        if not(tasklist):
            print('nothing was found')
            return 'nothing was found, let user try another word' 
        
        print(tasklist)
        return f'Success\n{tasklist}'
    else:
        print('error')
        return 'error'

def update_tasklist(id:str, update_display_name:str):
    '''
    updates the name of the tasklist
    
    ARGS:
    id: The id of the tasklist whose displayName the user wish to change 
    update_display_name: The new updated display name
    '''
    url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{id}'
    
    request_body = {
        'displayName': f'{update_display_name}'
    }

    try:
        response = requests.patch(url = url, headers = headers, json = request_body)
    except:
        print('update_tasklist_sending_error')
        return 'error'
    
    if response.status_code == 200:
        print('all good to go')
        return 'success'
    else:
        print('update_tasklist_response_code')
        print(response.status_code)
        return 'error'

#semi Test
def delete_tasklist(id:str):
    '''
    Deletes the tasklist with their ID
    
    ARGS:
    tasklist_id: The id of the tasklist the user wish to delete
    '''
    url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{id}'
    
    try:
        response = requests.delete(url = url, headers= headers)
    except:
        print('something went wrong sending the response, delete_tasklist')
        return 'error in sending response, delete_tasklist'
    
    if response.status_code == 204:
        print('success in deleting the tasklist, delete_tasklist')
        return 'success'
    else:
        print('response_code error, delete_tasklist')
        return 'error in response_code, delete_tasklist'

#Creating
def create_to_do(tasklist_id:str, To_Do_task:str):
    '''
    Creates a to do task for the tasklist using the ID 
    
    ARGS:
    tasklist_id: The id of the tasklisk in which the todo list will be created under
    '''
    
    url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{tasklist_id}/tasks'
    
    
    
#Testing to make model faster
def update_system_instruction(instruction:str):
    pass 



async def main():
    global headers 
    user = MA.Account(MA.azure_settings)
    headers = await user.get_user_token()

runs(main())