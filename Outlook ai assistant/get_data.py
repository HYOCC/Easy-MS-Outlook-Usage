import requests
from datetime import datetime, timedelta 
from configparser import SectionProxy
from azure.identity import  InteractiveBrowserCredential
from msgraph import GraphServiceClient
import configparser
import asyncio 

config = configparser.ConfigParser()
config.read(['config.cfg', 'config.dev.cfg'])
azure_settings = config['azure']
events = ''
headers = ''


class Account:
    settings: SectionProxy
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = InteractiveBrowserCredential(client_id = client_id, tenant_id = tenant_id, redirect_uri="http://localhost:8400")
        self.user_client = GraphServiceClient(self.device_code_credential, scopes=graph_scopes)

    async def get_user_token(self):
        global headers
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        headers = {
            'Authorization': f'Bearer {access_token.token}',
            'Prefer': 'outlook.timezone = "Eastern Standard Time"',
            'Content-Type': 'application/json'
        }
        return access_token.token


def get_events(start_date_time=None, end_date_time=None): 
    calendar_url = f'https://graph.microsoft.com/v1.0/me/calendarview?startdatetime={start_date_time}&enddatetime={end_date_time}&$select=subject,start,end,location'
    events = '' 
    
    if start_date_time and end_date_time:
        data = requests.get(calendar_url, headers=headers)
        for event in data.json()['value']: 
            events += f"Event: Title = {event['subject']}, Time = {event['start']['dateTime']} - {event['end']['dateTime']}, Location = {event['location']['displayName']}, Event ID = {event['id']}\n"
    else:
        data = requests.get('https://graph.microsoft.com/v1.0/me/events?$filter=type eq \'seriesMaster\'&$select=subject,start,end,location', headers=headers)
        for event in data.json()['value']: 
            events += f"Event: Title = {event['subject']}, Time = {event['start']['dateTime']} - {event['end']['dateTime']}, Location = {event['location']['displayName']}, Event ID = {event['id']}\n"
        data = requests.get(f'https://graph.microsoft.com/v1.0/me/events?$filter=type eq \'singleInstance\' and start/dateTime ge \'{datetime.now().isoformat()}\'&$select=subject,start,end,location', headers=headers)
        for event in data.json()['value']: 
            events += f"Event: Title = {event['subject']}, Time = {event['start']['dateTime']} - {event['end']['dateTime']}, Location = {event['location']['displayName']}, Event ID = {event['id']}\n"
    return events 
    
    
def create_event(event_name, start_date, end_date, start_time, end_time, location_name=None, categories=None, notes = None):
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
            request_body['location']['displayName'] = location_name
            
        if categories:
            request_body['categories'] = []
            request_body['categories'].append(categories)
            
                
        if notes:
            request_body['body'] = {}
            request_body['body']['contentType'] = 'HTML'
            request_body['body']['content'] = f'{notes}'
            
        response = requests.post(calendar_url, json=request_body, headers=headers)
        if response.status_code == 201:
            return 'Event created successfully!', response
            
        else:
            return 'Event not created successfully'


def delete_event(event_id):
    url = f'https://graph.microsoft.com/v1.0/me/events/{event_id}'
    response = requests.delete(url, headers=headers)
    print(response.status_code)
    return 'success in deleting event' if response.status_code == 204 else 'Not successful'

def Create_event_with_recurrence(event_name, start_date, end_date, start_time, end_time, range, interval, pattern_type, end_type, location_name=None, categories=None, daysOfWeek=None, dayOfMonth = None, numberOfOccurrences = None):
    
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
            'recurrence': {
                'pattern': {
                    'type': f'{pattern_type}',
                    'interval': f'{interval}'
                },
                'range': {
                    'type': f'{end_type}',
                    'startDate': f'{range[0]}'
                }
            }
        }

        if location_name:
            request_body['location'] = {}
            request_body['location']['displayName'] = location_name
            
        if categories:
            request_body['categories'] = []
            request_body['categories'].append(categories)
        
        if daysOfWeek:
            request_body['recurrence']['pattern']['daysOfWeek'] = daysOfWeek 
            
        if dayOfMonth:
            request_body['recurrence']['pattern']['dayOfMonth'] = dayOfMonth 
        
        try:
            if range[1]:
                request_body['recurrence']['range']['endDate'] = range[1] 
        except: 
            pass 
        
        if numberOfOccurrences:
            request_body['recurrence']['range']['numberOfOccurrences'] = numberOfOccurrences
        
        print(request_body)
        response = requests.post(calendar_url, json=request_body, headers=headers)
        
        if response.status_code == 201:
            return 'Event created successfully!', response
            
        else:
            return 'Event not created successfully', None 
        
        
        
def get_categories():
    global headers
    Category_url = 'https://graph.microsoft.com/v1.0/me/outlook/masterCategories/'
    Response = requests.get(Category_url, headers = headers)
    data = Response.json()
    
    if Response.status_code == 200:
        categories = [] 
        for category in data['value']:
            categories.append([category['id'], category['displayName'], category['color']])
        return categories
    else:
        return 'Not successful'


#Testing to create categories 
def create_categories(color, display_name):
    global headers 
    Create_category_url = 'https://graph.microsoft.com/v1.0/me/outlook/masterCategories'
    body_type = {
        'color' : color ,
        'displayName': display_name 
    }
    
    Response = requests.get(Create_category_url, headers = body_type)
    
    if Response.status_code == 201:
        return 'Successful'
    return 'Not successful'


#Add a create category function
 
user = Account(azure_settings)

async def run_data():
    await user.get_user_token()
    return None 




