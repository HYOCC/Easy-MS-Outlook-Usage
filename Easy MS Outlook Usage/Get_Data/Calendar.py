import requests
from datetime import datetime
from Get_Data.Auth.Microsoft_authy import get_headers

headers = ''

#Helper function to get the weekday of the date 
def get_weekday(date_time):
        date = datetime.fromisoformat(date_time).date()
        weekday = date.strftime('%A')
        return weekday   

#Gets only the series master event ID given a specifc time range, not tested
def get_recurring_event_id(start_date_time:str, end_date_time:str):
    global headers
    '''
    Gets the Series Master ID that is used to change every event under the recurring event
    
    ARGS:
    start_date_time: The start date and time to search for one of the occurences of the event. format of year-month-dayTmilitaryHour:minutes:seconds
    end_date_time: The end date and time to search for one of the occurences of the event format of year-month-dayTmilitaryHour:minutes:seconds
    
    returns the series master ID of the event 
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    
    print('get_recurring_event_id') #Log
    url = f'https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={start_date_time}&endDateTime={end_date_time}&$select=seriesMasterId,subject,start,end,location'

    event_list = []#Creates a empty list to store events
    
    series_data = requests.get(url, headers=headers)
    
    for series_event in series_data.json()['value']:
        #If the event contains a series master within the time range, get its seriesmaster id
        if series_event['seriesMasterId'] is not None: 
            event_list.append(f"Event: Title = {series_event['subject']}, Time = {series_event['start']['dateTime']} {get_weekday(series_event['start']['dateTime'])} - {series_event['end']['dateTime']} {get_weekday(series_event['end']['dateTime'])}, Location = {series_event['location']['displayName']}, Series Master Event ID: {series_event['seriesMasterId']}")

    return event_list

#Gets only the Instance given a specifc time range
def get_single_event_id(start_date_time:str, end_date_time:str):
    global headers
    '''
    Gets the instance event ID of all the instance event under a time range 
    
    ARGS:
    start_date_time: The start date and time to search for the event. format of year-month-dayTmilitaryHour:minutes:seconds
    end_date_time: The end date and time to search for the event format of year-month-dayTmilitaryHour:minutes:seconds
    
    returns all the instance events 
    '''
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
        
    print('get_single_event_id') #Log
    print(start_date_time)#Log
    print(end_date_time)#Log
    url = f'https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={start_date_time}&endDateTime={end_date_time}&$select=subject,start,end,location'
    
    event_list = []#Creates a empty list to store events
    
    event_data = requests.get(url, headers=headers)
    
    
    if event_data.status_code == 200:
        for event in event_data.json()['value']:
            event_list.append(f"Event: Title = {event['subject']}, Time = {event['start']['dateTime']} {get_weekday(event['start']['dateTime'])} - {event['end']['dateTime']} {get_weekday(event['end']['dateTime'])}, Location = {event['location']['displayName']}, Event ID: {event['id']}")
    else:
        print('Not successful')
        print(start_date_time)
        print(end_date_time)
        return 'Not succcessful'
        
    return event_list


#Gets the events of a time range
def get_events(start_date_time:str, end_date_time:str):
    global headers 
    '''
    Gets all the events in the specified time frame for displaying to user ONLY. Does not display event_id
    
    If the starting date/time is not specificed, ALWAYS go from the current date time.
    If user wants all of their event, go from current time and date to next month 
    If the user asks for next event, use get_events that goes from today, to tomorrow to the next day until there is a event.
    Convert the time to AM/PM format
    If user requests events on a specific date, omit date in output
    Include what day of the week it is
    Include location and description if applicable
    If the user asks for next event, use get_events that goes from today, to tomorrow to the next day until there is a event.
    
    ARGS:
    start_date_time: The user specified starting time in the format of year-month-dayTmilitaryHour:minutes:seconds 
    end_date_time: The user specified end time frame in the format of year-month-dayTmilitaryHour:minutes:seconds 
    
    Returns a list of event that is sorted already chronologically
    ''' 
    
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    
    print('get_events')#Logging
    
    def convert_event_to_time(event): #gets only the starting time of a event
        time_start_index = event.index('Time') + 7
        time_end_index = time_start_index + 28
        
        return event[time_start_index:time_end_index]    
    
    url = f'https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={start_date_time}&endDateTime={end_date_time}&$select=subject,start,end,location,categories,body'
    event_list = [] 
    event_data = requests.get(url = url, headers=headers) 
    if event_data.status_code == 200:
        for event in event_data.json()['value']:
            event_start_date_time = event['start']['dateTime']
            event_end_date_time = event['end']['dateTime']
            
            #Adds the event base on their time of occurence
            if not(event_list):
                event_list.append(f"Event: Title = {event['subject']}, Time = {event_start_date_time} {get_weekday(event_start_date_time)} - {event_end_date_time} {get_weekday(event_end_date_time)}, Location = {event['location']['displayName']}")
            else: 
                i = len(event_list)
                
                current_addition = f"Event: Title = {event['subject']}, Time = {event_start_date_time} {get_weekday(event_start_date_time)} - {event_end_date_time} {get_weekday(event_end_date_time)}, Location = {event['location']['displayName']}"
                current_addition_converted = convert_event_to_time(current_addition)
                
                while i > 0 and current_addition_converted < convert_event_to_time(event_list[i - 1]):
                    i -= 1
                event_list.insert(i, current_addition)
    else:
        print('Error in get_events')
        return 'Error in get_events'
    print(event_list)
    return event_list
    
    
def create_event(event_name:str, start_date:str, end_date:str, start_time:str, end_time:str, location_name:str=None, categories:str=None, notes:str = None):
    global headers
    '''
    Create the event(s) in the Outlook calendar. Call this whenever the user requests an single instance event to be added/created
    If the user wants to assign the event to a unexisting category, ask the user for a color if not provided and use this dictionary {category_colors} that corresponds to the preset of the color. Create the category, then use get_categories and assign the event to the newly created category. If the color isnt in the dictionary, use the closest relating one
    For assigning the event to a category, use get_category first to get a list of existing, else ask the user if they wanna create a new one using create_category and assign the event to that category
    
    
    ARGS:
    event_name: The event's name
    start_date: The event's start date in year-month-date format
    end_date: The event's end date in year-month-date format
    start_time: The event's start time in hr:min:sec format
    end_time: The event's end time in hr:min:sec format
    location_name: The event's location
    categories: The event's category, look for existing category first if there is no existing category, tell the user to specify which further
    notes: The event's description such as if user wants to add a little info regarding the event.
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

    Deletes an event by using the 'Event ID' or 'seriesmasterID'. Use get_single_event_id or get_recurring_event_id to get proper event ID first
    
    ARGS:
    event_id: The event id or seriesmasterID
    
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
        print('success')
        print(request_body)
        return 'Event created successfully!'
        
    else:
        print('Not success')
        print(request_body)
        return 'Event not created successfully' 
        
#TESTING
def update_event(id:str, event_name:str, start_date:str, end_date:str, start_time:str, end_time:str, location_name:str=None, categories:str=None, notes:str = None):
    global headers
    '''
    Updates the information of the event using the id, Only for Instance events. use get_single_event_id to get the event ID first

    
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
    print('update_event')
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

#Testing
def update_event_with_recurrence(id:str, event_name:str=None, start_date:str=None, end_date:str=None, start_time:str=None, end_time:str=None, pattern_type:str=None, interval:int=None, end_type:str=None, recurring_end_date:str=None, location_name:str=None, categories:str=None, daysOfWeek:list[str]=None, dayOfMonth:int = None, numberOfOccurrences:int = None, notes:str = None):
    global headers
    '''    
    Updates every instance of the event that is recurring using the recurring event ID. For ALL of the instance event within the recurring.  use get_recurring_event_id to get the event ID first
    
    ARGS:
    id: the id of the recurring event
    event_name: The event's name
    start_date: The event's start date in year-month-date format. If start_date is given, start_time is required 
    end_date: The event's end date in year-month-date format. If end_date is given, end_time is required 
    start_time: The event's start time in hr:min:sec format If start_time is given, start_date is required
    end_time: The event's end time in hr:min:sec format. If end_time is given, end_date is required 
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
        
    print('update_event_with_recurrence') #Log
    url = f'https://graph.microsoft.com/v1.0/me/events/{id}'
    
    event_detail = requests.get(url=url,headers=headers).json() #Gets the event detail of the id and converts it from json to python readable
    print(event_detail) #LOG
    
    request_body = {
        'subject': event_detail['subject'],
        'start': {
            'dateTime': event_detail['start']['dateTime'],
            'timeZone': 'America/New_York'
        },
        'end': {
            'dateTime': event_detail['end']['dateTime'],
            'timeZone': 'America/New_York'
        },
        'location':{
            'displayName': event_detail['location']['displayName']
        },
        'recurrence': {
            'pattern': {
                'type': event_detail['recurrence']['pattern']['type'],
                'interval': event_detail['recurrence']['pattern']['interval'],
                'daysOfWeek': event_detail['recurrence']['pattern']['daysOfWeek'],
                'firstDayOfWeek': event_detail['recurrence']['pattern']['firstDayOfWeek'],
                'dayOfMonth': event_detail['recurrence']['pattern']['dayOfMonth']
            },
            'range': {
                'type': event_detail['recurrence']['range']['type'],
                'startDate': event_detail['recurrence']['range']['startDate'],
                'endDate': event_detail['recurrence']['range']['endDate'], 
                'type': event_detail['recurrence']['range']['type'],
                'numberOfOccurrences': event_detail['recurrence']['range']['numberOfOccurrences']
            }
        },
        'categories': event_detail['categories'],
        'bodyPreview': event_detail['bodyPreview']
    }

    if event_name:
        request_body['subject'] = event_name
    
    if start_date: 
        request_body['start']['dateTime'] = f'{start_date}{event_detail['start']['dateTime'][11:]}'
        
    if start_time:
        request_body['start']['dateTime'] = f'{event_detail['start']['dateTime'][:12]}{start_time}'
        
    if start_date and start_time:
        request_body['start']['dateTime'] = f'{start_date}T{start_time}'
    
    if end_date: 
        request_body['end']['dateTime'] = f'{end_date}{event_detail['end']['dateTime'][11:]}'
    
    if end_time:
        request_body['end']['dateTime'] = f'{event_detail['end']['dateTime'][:12]}{end_time}'
        
    if end_date and end_time:
        request_body['end']['dateTime'] = f'{end_date}T{end_time}'
        
    if pattern_type:
        request_body['recurrence']['pattern']['type'] = pattern_type 
    
    if interval: 
        request_body['recurrence']['pattern']['interval'] = interval
    
    if end_type:
        request_body['recurrence']['range']['type'] = end_type 
    
    if recurring_end_date:
        request_body['recurrence']['range']['endDate'] = recurring_end_date
    
    if location_name: 
        request_body['location']['displayName']= location_name
    
    if categories:
        request_body['catergories'] = categories
    
    if notes:
        request_body['bodyPreview'] = notes 
    
    if dayOfMonth:
        request_body['recurrence']['pattern']['dayOfMonth'] = dayOfMonth
    
    if numberOfOccurrences:
        request_body['recurrence']['pattern']['numberOfOccurrences'] = numberOfOccurrences
        
    #Log
    print(request_body)
    
    try: 
        response = requests.patch(url = url, json=request_body, headers=headers)
    except:
        print('update_event_with_recurrence sending response error')
        return 'error'
    #If it successfully goes through
    if response.status_code == 200:
        return 'success in updating event with recurrence'
    else:
        print('update_event_with_recurrence response code error')
        print(response.status_code)
        return 'error'    

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
    print('get_category')#Logging
    Category_url = 'https://graph.microsoft.com/v1.0/me/outlook/masterCategories/'
    Response = requests.get(Category_url, headers = headers)
    data = Response.json()
    
    if Response.status_code == 200:
        categories = [] 
        for category in data['value']:
            categories.append([category['id'], category['displayName'], category['color']])
        print(categories)
        return categories
    else:
        return 'Not successful'
    
def create_categories(color_preset:str, display_name:str):
    global headers
    '''
    When a user wants to add a event to a unexisting category, create that category
    The user will give a color for the category and you will look for it in {"Red": "Preset0","Orange": "Preset1","Brown": "Preset2","Yellow": "Preset3","Green": "Preset4","Teal": "Preset5","Olive": "Preset6","Blue": "Preset7","Purple": "Preset8","Cranberry": "Preset9","Steel": "Preset10","DarkSteel": "Preset11","Gray": "Preset12","DarkGray": "Preset13","Black": "Preset14","DarkRed": "Preset15","DarkOrange": "Preset16","DarkBrown": "Preset17","DarkYellow": "Preset18","DarkGreen": "Preset19","DarkTeal": "Preset20","DarkOlive": "Preset21","DarkBlue": "Preset22","DarkPurple": "Preset23","DarkCranberry": "Preset24"}
    
    ARGS:
    color_preset: The preset of the color
    display_name: The name for the category
    
    returns None 
    '''
    print('create_categories')#Log
    print(color_preset)#Log
    print(display_name)#Log
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    Create_category_url = 'https://graph.microsoft.com/v1.0/me/outlook/masterCategories'
    body_type = {
        'color' : f'{color_preset}',
        'displayName': f'{display_name}' 
    }
    
    response = requests.post(url=Create_category_url, headers=headers, json=body_type)
    
    if response.status_code == 201:
        print('success in creating category')
        return 'Successful'
    else: 
        print('not success in creating category')
        print(response.status_code)
        return 'Let user know not successful'
    
def delete_categories(category_id:str):
    global headers
    '''
    Delete a category using the category ID
    
    ARGS:
    category_id: The category ID to be used
    '''
    
    print('delete_category')#Log
    #If the user signed in and authenticates it, update header only once throughout this program
    if not(headers):
        headers = get_headers()
    
    url = f'https://graph.microsoft.com/v1.0/me/outlook/masterCategories/{category_id}'
    #Sends the information to the url for the category to be deleted
    response = requests.delete(url = url, headers = headers)
    
    if response.status_code == 204:
        print('success in deleting category')
        return 'success in deleting category'
    else:
        print('Error in deleting category')
        return 'error in deleting category'
    

