import requests
from datetime import datetime
from Get_Data.Auth.Microsoft_authy import get_headers

headers = ''

#Helper function to get the weekday of the date 
def get_weekday(date_time):
        date = datetime.fromisoformat(date_time).date()
        weekday = date.strftime('%A')
        return weekday   

#rEVAMPING TO GOOGLE Function calling 
def get_events(start_date_time:str, end_date_time:str):
    global headers 
    '''
    Gets all the events in the specified time frame
    
    ARGS:
    start_date_time: The user specified starting time in the format of year-month-dayTmilitaryHour:minutes:seconds 
    end_date_time: The user specified end time frame in the format of year-month-dayTmilitaryHour:minutes:seconds
    
    Returns the set of event that is listed within the time frame and all their informations, the time is in the format of year-month-dayTmilitaryHour:minutes:seconds and they are not chronological order
    ''' 
    print('get_event')
    
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()    
    
     
    events = ''
    calendar_url_single = f'https://graph.microsoft.com/v1.0/me/events?$filter=type eq \'singleInstance\' and start/dateTime ge \'{start_date_time}\' and end/dateTime le \'{end_date_time}\'&$select=subject,start,end,location'
    calendar_url_series = f'https://graph.microsoft.com/v1.0/me/events?$filter=type eq \'seriesMaster\'&$select=subject'

    if start_date_time and end_date_time:
        #Getting only the first occurrence from a recurring event 
        series_data = requests.get(calendar_url_series, headers=headers)
        for series_event in series_data.json()['value']:#Goes through each recurrence event
            series_master_id = series_event['id'] #Gets their ID
            instance_url = f'https://graph.microsoft.com/v1.0/me/events/{series_master_id}/instances?startDateTime={start_date_time}&endDateTime={end_date_time}&$select=subject,start,end,location'
            instance_data = requests.get(instance_url, headers=headers).json() 
            try:
                if instance_data['value'][0]: #Only gets the first instance' event and adds it to event 
                    first_instance = instance_data['value'][0] 
                    event_start_date_time = first_instance['start']['dateTime']
                    event_end_date_time = first_instance['end']['dateTime']
                    events += f"Event: Title = {first_instance['subject']}, Time = {event_start_date_time} {get_weekday(event_start_date_time)} - {event_end_date_time} {get_weekday(event_end_date_time)}, Location = {first_instance['location']['displayName']}, Event ID = {first_instance['id']}, Type = Recurring\n"
            except: 
                pass
        #Gets only the single instance events 
        singe_data = requests.get(calendar_url_single, headers=headers)
        for event in singe_data.json()['value']: 
            event_start_date_time = event['start']['dateTime']
            event_end_date_time = event['end']['dateTime']
            events += f"Event: Title = {event['subject']}, Time = {event_start_date_time} {get_weekday(event_start_date_time)} - {event_end_date_time} {get_weekday(event_end_date_time)}, Location = {event['location']['displayName']}, Event ID = {event['id']}, Type = NonRecurring\n"
    else:
        #Getting only the first occurrence from a recurring event 
        series_data = requests.get(calendar_url_series, headers=headers)
        if series_data.status_code == 200:
            for event in series_data.json()['value']: 
                events += f"Event: Title = {event['subject']}, Event ID = {event['id']}, Type = Recurring\n"
            #Gets only the single instance events 
            singe_data = requests.get(f'https://graph.microsoft.com/v1.0/me/events?$filter=type eq \'singleInstance\' and start/dateTime ge \'{datetime.now().isoformat()}\'&$select=subject,start,end,location', headers=headers)
            for event in singe_data.json()['value']: 
                event_start_date_time = event['start']['dateTime']
                event_end_date_time = event['end']['dateTime']
                events += f"Event: Title = {event['subject']}, Event ID = {event['id']}, Type = NonRecurring\n"
        else:
            print('response_code error, get_events')
            
            #DEBUG
            print(headers)
            return 'response_code error, get_events'
    return events 
    
    
def create_event(event_name:str, start_date:str, end_date:str, start_time:str, end_time:str, location_name:str=None, categories:str=None, notes:str = None):
    global headers
    '''
    Create the event(s) in the Outlook calendar. Call this whenever the user requests an event to be added/created
    
    ARGS:
    event_name: The event's name
    start_date: The event's start date in year-month-date format
    end_date: The event's end date in year-month-date format
    start_time: The event's start time in hr:min:sec format
    end_time: The event's end time in hr:min:sec format
    location_name(optional): The event's location
    categories(optional): The event's category, look for existing category first if there is no existing category, tell the user to specify which further
    notes(optional): The event's description such as if user wants to add a little info regarding the event.
    '''
    print('create_event')
    
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers() 
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
        return 'Event created successfully!'
    else:
        return 'Event not created successfully'


def delete_event(event_id:str):
    global headers
    '''
    Deletes an event by using the 'Event ID' or 'event recurring ID'
    
    ARGS:
    event_id: The event id or event recurring ID
    
    '''
    print('delete_event')
    
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    url = f'https://graph.microsoft.com/v1.0/me/events/{event_id}'
    response = requests.delete(url, headers=headers)
    return 'success in deleting event' if response.status_code == 204 else 'Not successful'

def Create_event_with_recurrence(event_name:str, start_date:str, end_date:str, start_time:str, end_time:str, pattern_type:str, interval:int=1, end_type:str='noEnd', recurring_end_date:str=None, location_name:str=None, categories:str=None, daysOfWeek:list[str]=None, dayOfMonth:int = None, numberOfOccurrences:int = None, notes:str = None):
    global headers
    '''
    Creates an event with the events reccuring either weekly or monthly
    
    ARGS:
    event_name: The event's name
    start_date: The event's start date in year-month-date format
    end_date: The event's end date in year-month-date format
    start_time: The event's start time in hr:min:sec format
    end_time: The event's end time in hr:min:sec format
    recurring_end_date: The ending date of this reccuring event, NOT the instance, the recurring itself
    interval: The number of units between occurrences.
    pattern_type: The type of reccurence the user wants which can be 'daily', 'weekly', 'absoluteMonthly', 'absoluteYearly'
    end_type: How the user wants the recurrance to end which can be 'numbered', 'endDate'. Default to 'noEnd'. if the user wants to create event on multiple days in a week just for one week, use 'numbered' and set numberofoccurrence to 1. If user has a date in mind which the recurrence should end, use 'endDate'. Else if the user wants it to repeat a certain time, user 'numbered'.
    daysOfWeek: The day of the week that the user wants the event to be repeated on if the type parameter is weekly. It can be multiple days which can be 'monday','tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'. format it into [], ex. ['monday', 'tuestday'], ['monday'].
    dayOfMonth: The day of the month that the user wants the event to be repeated on, if none are specified, assume its the current date
    location_name: The event's location
    categories: The event's category, such as School events, club events etc.
    notes: The event's description such as if user wants to add a little info regarding the event.
    numberOfOccurrences: If end_type is numbered, this is the number of times that the set of event repeat for.
    
    '''
    print('Create_event_with_recurrence')
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
        
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
                'type': f'{pattern_type.lower()}',
                'interval': f'{int(interval)}'
            },
            'range': {
                'type': f'{end_type}',
                'startDate': f'{start_date}'
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
        request_body['recurrence']['pattern']['daysOfWeek'] = [day.lower() for day in daysOfWeek]
        
    if dayOfMonth:
        request_body['recurrence']['pattern']['dayOfMonth'] = dayOfMonth 
        
    if recurring_end_date:
        request_body['recurrence']['range']['endDate'] = recurring_end_date
    
    if numberOfOccurrences:
        request_body['recurrence']['range']['numberOfOccurrences'] = numberOfOccurrences
        
    if notes:
        request_body['body'] = {}
        request_body['body']['contentType'] = 'HTML'
        request_body['body']['content'] = f'{notes}'
    
    response = requests.post(calendar_url, json=request_body, headers=headers)
    
    if response.status_code == 201:
        return 'Event created successfully!'
        
    else:
        return 'Event not created successfully' 
        
#TESTING
def update_event(id:str, event_name:str, start_date:str, end_date:str, start_time:str, end_time:str, location_name:str=None, categories:str=None, notes:str = None):
    global headers
    '''
    Updates the information of the event using the id
    
    ARGS:
    id: the id of the event
    event_name: The event's name
    start_date: The event's start date in year-month-date format
    end_date: The event's end date in year-month-date format
    start_time: The event's start time in hr:min:sec format
    end_time: The event's end time in hr:min:sec format
    location_name(optional): The event's location
    categories(optional): The event's category, look for existing category first if there is no existing category, tell the user to specify which further
    notes(optional): The event's description such as if user wants to add a little info regarding the event.
    '''
    
    url = f'https://graph.microsoft.com/v1.0/me/events/{id}'
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    
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
        
    try:
        response = requests.patch(url = url, headers=headers, json=request_body)
    except: 
        print('updating error')
        return 'updating error, have the user repeat it again'
    
    if response.status_code == 200:
        print('successfully updated!')
        return 'successfully updated!'
    else:
        print('updating event error')
        return 'updating error, have the user repeat it again'

    
        
def get_categories():
    global headers
    '''
    Gets all of the existing categories information such as name, color and id

    ARGS:
    None
    
    Returns the categories in a list    
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    print('get_categories')
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

#Testing
def update_event_with_recurrence(id:str, event_name:str, start_date:str, end_date:str, start_time:str, end_time:str, pattern_type:str, interval:int=1, end_type:str='noEnd', recurring_end_date:str=None, location_name:str=None, categories:str=None, daysOfWeek:list[str]=None, dayOfMonth:int = None, numberOfOccurrences:int = None, notes:str = None):
    global headers
    '''
    Updates event that is recurring 
    
    ARGS:
    id: the id of the recurring event
    event_name: The event's name
    start_date: The event's start date in year-month-date format
    end_date: The event's end date in year-month-date format
    start_time: The event's start time in hr:min:sec format
    end_time: The event's end time in hr:min:sec format
    recurring_end_date: The ending date of this reccuring event, NOT the instance, the recurring itself
    interval: The number of units between occurrences.
    pattern_type: The type of reccurence the user wants which can be 'daily', 'weekly', 'absoluteMonthly', 'absoluteYearly'
    end_type: How the user wants the recurrance to end which can be 'numbered', 'endDate'. Default to 'noEnd'. if the user wants to create event on multiple days in a week just for one week, use 'numbered' and set numberofoccurrence to 1. If user has a date in mind which the recurrence should end, use 'endDate'. Else if the user wants it to repeat a certain time, user 'numbered'.
    daysOfWeek: The day of the week that the user wants the event to be repeated on if the type parameter is weekly. It can be multiple days which can be 'monday','tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'. format it into [], ex. ['monday', 'tuestday'], ['monday'].
    dayOfMonth: The day of the month that the user wants the event to be repeated on, if none are specified, assume its the current date
    location_name: The event's location
    categories: The event's category, such as School events, club events etc.
    notes: The event's description such as if user wants to add a little info regarding the event.
    numberOfOccurrences: If end_type is numbered, this is the number of times that the set of event repeat for.
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    url = f'https://graph.microsoft.com/v1.0/me/events/{id}'

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
                'type': f'{pattern_type.lower()}',
                'interval': f'{int(interval)}'
            },
            'range': {
                'type': f'{end_type}',
                'startDate': f'{start_date}'
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
        request_body['recurrence']['pattern']['daysOfWeek'] = [day.lower() for day in daysOfWeek]
        
    if dayOfMonth:
        request_body['recurrence']['pattern']['dayOfMonth'] = dayOfMonth 
        
    if recurring_end_date:
        request_body['recurrence']['range']['endDate'] = recurring_end_date
    
    if numberOfOccurrences:
        request_body['recurrence']['range']['numberOfOccurrences'] = numberOfOccurrences
        
    if notes:
        request_body['body'] = {}
        request_body['body']['contentType'] = 'HTML'
        request_body['body']['content'] = f'{notes}'
    
    try: 
        response = requests.patch(url = url, json=request_body, headers=headers)
    except:
        print('update_event_with_recurrence sending response error')
        return 'error'
        
    if response.status_code == 200:
        return 'success in updating event with recurrence'
    else:
        print('update_event_with_recurrence response code error')
        return 'error'    
    

#Testing to create categories 
def create_categories(color:str, display_name:str):
    global headers
    '''
    When a user wants to add a event to a unexisting category, create that category
    
    ARGS:
    color: The preset of the color. 
    display_name: The name for the category
    
    returns None 
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    Create_category_url = 'https://graph.microsoft.com/v1.0/me/outlook/masterCategories'
    body_type = {
        'color' : color,
        'displayName': display_name 
    }
    
    #Recently changed 
    Response = requests.get(Create_category_url, headers, body_type)
    
    if Response.status_code == 201:
        return 'Successful'
    return 'Not successful'