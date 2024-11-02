import requests
from datetime import datetime
from Get_Data.Auth.Microsoft_authy import get_headers

 
headers = '' 

#Helper function to get the weekday of the date 
def get_weekday(date_time):
        date = datetime.fromisoformat(date_time).date()
        weekday = date.strftime('%A')
        return weekday   
 
#Semi tested
def create_tasklist(displayName:str):
    global headers
    '''
    Creates a todo category, for example a task lisk for life or homework etc 
    
    ARGS:
    displayname: The name of the category
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
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


#Semi tested
def get_tasklist(name:str):
    global headers
    '''
    Gets the tasklist information using the name off the tasklist
    
    ARGS:
    name: the name of the tasklist 
    
    returns the id 
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
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

#Not extensively tested
def update_tasklist(id:str, update_display_name:str):
    global headers
    '''
    updates the name of the tasklist
    
    ARGS:
    id: The id of the tasklist whose displayName the user wish to change 
    update_display_name: The new updated display name
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
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
    global headers
    '''
    Deletes the tasklist with their ID
    
    ARGS:
    tasklist_id: The id of the tasklist the user wish to delete
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
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