import requests
from datetime import datetime, timedelta 
from configparser import SectionProxy
from azure.identity import  InteractiveBrowserCredential
from msgraph import GraphServiceClient
import configparser
from asyncio import run as runs

#Starts the configperser and uses it to read 'config.cfg' file for the info side and process it 
config = configparser.ConfigParser()
config.read(['config.cfg', 'config.dev.cfg'])
#Use the process data under the liner 'azure' in the file as the azure setting
azure_settings = config['azure']
headers = ''

#The account class 
class Account:
    #Creates a sectionproxy class and assign it 'settings'
    settings: SectionProxy
    #Creates the graph api client and assigns it to 'user_client'
    user_client: GraphServiceClient

    #Uses the config setting to get the client and tenant id for authorization purpose then gets the permission allowed
    def __init__(self, config: SectionProxy):
        self.settings = config
        self.client_id = self.settings['clientId']
        self.tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')
        
        #Starts a browser for authentication purposes that uses the azure id for usage and comomn tenant_id and redirects the user to the url of the authrization

        self.device_code_credential = InteractiveBrowserCredential(client_id = self.client_id, tenant_id = self.tenant_id, redirect_uri="http://localhost:8400")
        
            
        #Creates the graph client that has been verified
        self.user_client = GraphServiceClient(self.device_code_credential, scopes=graph_scopes)

    #Gets the user token for auhorization usage of outlook function
    async def get_user_token(self):
        global headers #Globalized headers so it can be used outside of the class 
        
        
        graph_scopes = self.settings['graphUserScopes'] #What the system is allowed to have access to 
        try:
            access_token = self.device_code_credential.get_token(graph_scopes) #uses the verified credentials to get the authorization token
        except:
            #If accessing token is not valid, prompt the user to log in again
            print('try again')
            self.device_code_credential = InteractiveBrowserCredential(client_id = self.client_id, tenant_id = self.tenant_id, redirect_uri="http://localhost:8400")
            try:
                access_token = self.device_code_credential.get_token(graph_scopes) #uses the verified credentials to get the authorization token
            except:
                return 'Try again another time'
        headers = { #Sets the header with the access_token to be used anywhere
            'Authorization': f'Bearer {access_token.token}',
            'Prefer': 'outlook.timezone = "Eastern Standard Time"',
            'Content-Type': 'application/json'
        }
        
        return access_token.token

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
    


def create_to_do(tasklist_id:str):
    '''
    Creates a to do task for the tasklist using the ID 
    
    ARGS:
    tasklist_id: The id of the tasklisk in which the todo list will be created under
    '''
    
    url = f'https://graph.microsoft.com/v1.0/me/todo/lists/{tasklist_id}/tasks'
    
    
    


async def main():
    user = Account(azure_settings)
    await user.get_user_token()
    get_tasklist('Homeworks')

runs(main())