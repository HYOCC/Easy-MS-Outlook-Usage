from Get_Data.Auth.Microsoft_authy import get_headers_for_todo 
import requests

headers = ''

#ToDO- sort by completed and uncompleted status
def get_task_in_tasklist(tasklist_ID:str):
    global headers
    '''
    Gets all the task in a tasklist of the specified ID. 
    
    ARGS:
    tasklist_ID: The ID of the tasklist which is checked for tasks
    
    returns all the task that is not marked 'completed' in the tasklist 
    ''' 
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers_for_todo()
    print('get_task_in_tasklist')#Log
    url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{tasklist_ID}/tasks?$orderby=dueDateTime/dateTime desc&$select=id, status, importance, categories, body, dueDateTime'
    
    response_data = requests.get(url=url, headers=headers) #Gets the data
    
    if response_data.status_code == 200:
        to_do_list = []
        for to_do in response_data.json()['value']: 
            if 'dueDateTime' in to_do: #Adds the task name, due date, importance, status, and id 
                to_do_list.append(f'task name: {to_do['title']}, Due Date: {to_do['dueDateTime']}, importance: {to_do['importance']}, status: {to_do['status']}, ID: {to_do['id']}')
            else:
                to_do_list.append(f'task name: {to_do['title']}, Due Date: None, importance: {to_do['importance']}, status: {to_do['status']}, ID: {to_do['id']}')
        return to_do_list 
    else:
        print('error in status code, get_task_in_tasklist')
        print(response_data.status_code)
        print(response_data.text)
        return 'error'

#Kind of tested
def create_task_in_tasklist(task_name:str, due_date:str, due_time:str, importance:str='normal', description:str=None, tasklist_id:str='AQMkADAwATM0MDAAMS03ZTJlLTEyMDYtMDACLTAwCgAuAAADPz8ABZBfyUVFAK-hrjlV5YV4AQBjJ2kw_T2PSZcJpUcTo1DmAAACARIAAAA='):
    global headers
    '''
    
    Creates a task under a tasklist using the ID NOT the names. Look for implied clues such as when user wants to add a homework, look for a tasklist called homework first
    
    ARGS:
    task_name: The name of the task 
    tasklist_ID: The specified ID of the tasklist to create the task under. NOT THE NAME, the ID. Default to Broad Tasklist
    description: The description of the task if provided
    due_date: The due date for the task. Format in year-month-date 
    due_time: The due time for the task. Form in hr:min:sec
    importance: How urgent the task is. Values can be 'low', 'normal', 'high'. Default to 'normal' 
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers_for_todo()
    print('create_task_in_tasklist ')#Log
    print(tasklist_id)#Log 
    url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{tasklist_id}/tasks'
    
    request_body = {
        'title': task_name, 
        'dueDateTime': {
            'dateTime': f'{due_date}T{due_time}', 
            'timeZone':'America/New_York'
        },
        'importance': importance 
        
    }
    
    if description:
        request_body['body'] = {'content':description, 'contentType':'String'}
        
    response = requests.post(url = url, json=request_body, headers=headers)
    
    if response.status_code == 201:
        print('success') 
        return 'successful'
    else:
        print('error')
        print(response.status_code)
        print(response.text)
        return 'error in creating task'

#Kind of tested 
def update_task_in_tasklist(task_ID:str, tasklist_id:str, new_task_name:str=None, new_due_time:str=None, new_due_date:str=None, new_importance:str=None, new_description:str=None, new_status:str=None):
    global headers
    '''
    Updates a task within a tasklist
    
    ARGS:
    task_ID: The ID of the task that the user wants to change about 
    tasklist_id: The specified ID of the tasklist that the task is under. NOT THE NAME, the ID. Default to Broad Tasklist
    new_task_name: The new task name 
    new_due_time: The new due time. If there is a new due time, there must be a new due date too 
    new_due_date: The new due date. If there is a new due date, there must be a new due time too
    new_importance: New importance
    new_status: The newly updated status. Values can only be 'notStarted', 'inProgress', 'completed', 'waitingOnOthers', 'deferred'. Pick one that is closest to what the user wants
    new_description: The new description of the task
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers_for_todo()
    print('update_task_in_tasklist ')#Log
    url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{tasklist_id}/tasks/{task_ID}' 
    
    request_body = {}
    
    if new_task_name:
        request_body['title'] = new_task_name
    
    if new_due_date or new_due_time:
        request_body['dueDateTime'] = {'dateTime': f'{new_due_date}T{new_due_time}', 'timeZone':'America/New_York'}  
    
    if new_importance:
        request_body['importance'] = new_importance 
        
    if new_description:
        request_body['body'] = {'content': new_description, 'contentType':'String'}
    
    if new_status:
        request_body['status'] = new_status
    
    response = requests.patch(url = url, json=request_body, headers=headers) 
    
    if response.status_code == 200:
        print('success')
        return 'all good to go'
    else:
        print('not successful')
        print(response.status_code + '\n' + response.text)
        return 'Error in updating task'
    