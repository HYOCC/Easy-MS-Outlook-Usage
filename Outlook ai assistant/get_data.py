import requests
from datetime import datetime, timedelta 
from configparser import SectionProxy
from azure.identity import  InteractiveBrowserCredential
from msgraph import GraphServiceClient
import configparser

config = configparser.ConfigParser()
config.read(['config.cfg', 'config.dev.cfg'])
azure_settings = config['azure']
events = ''



class Account:
    settings: SectionProxy
    user_client: GraphServiceClient
    ENDPOINT = "https://graph.microsoft.com/v1.0"

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = InteractiveBrowserCredential(client_id = client_id, tenant_id = tenant_id, redirect_uri="http://localhost:8400")
        self.user_client = GraphServiceClient(self.device_code_credential, scopes=graph_scopes)

    async def get_user_token(self):
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        self.token = access_token.token
        return self.token

    async def get_events(self): 
        global events 

        calendar_url = f"{self.ENDPOINT}/me/events?$select=subject,start,end,location"
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Prefer': 'outlook.timezone = "Eastern Standard Time"',
            'Content-Type': 'application/json'
        }
        
        data = requests.get(calendar_url, headers=headers)
        for event in data.json()['value']:
            events += f"Title: {event['subject']}, Time: {event['start']['dateTime']} - {event['end']['dateTime']}\n"
        return events 
    
    
def create_event(event_name, start_date, end_date, start_time, end_time, location_name=None, categories=None, recurrence=False, reccurence_pattern=None, reccurence_range=None, reccurence_interval=None, reccurence_week = None):
        calendar_url = 'https://graph.microsoft.com/v1.0/me/events'
        request_body = {
            'subject': f'{event_name}',
            'start': {
                'dateTime': f'{start_date}T{start_time}',
                'timeZone': 'America/New_York'
            },
            'end': {
                'dateTime': f'{end_date}T{end_time}',
                'timeZone': 'America/New_York'
            },
        }
        if location_name:
            request_body['location'] = {}
            request_body['location']['display_name'] = location_name
            
        if categories:
            request_body['categories'] = []
            request_body['categories'].append(categories)
            
        if recurrence:
            request_body['reccurence'] = {} 
            request_body['reccurence']['pattern'] = {}
            request_body['reccurence']['pattern']['type'] = reccurence_pattern
            request_body['reccurence']['pattern']['interval'] = reccurence_interval
            request_body['reccurence']['pattern']['days_of_week'] = reccurence_week
            request_body['reccurence']['range'] = {}
            request_body['reccurence']['range']['type'] = 'endDate'
            request_body['reccurence']['range']['start_date'] = reccurence_range[0]
            request_body['reccurence']['range']['end_date'] = reccurence_range[1]   
            
             
            
    
        headers = {
            'Authorization': f'Bearer {token}',
            'Prefer': 'outlook.timezone = "Eastern Standard Time"',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(calendar_url, json=request_body, headers=headers)
        if response.status_code == 201:
            print('Event created successfully!')
        else:
            print('not successful')
        
user = Account(azure_settings)

async def run_data():
    global token 
    token = await user.get_user_token()
    events = await user.get_events()
    return events 







