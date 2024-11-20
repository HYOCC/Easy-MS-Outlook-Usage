from configparser import SectionProxy
from azure.identity import  InteractiveBrowserCredential
from msgraph import GraphServiceClient
import configparser

#Starts the configperser and uses it to read 'config.cfg' file for the info side and process it 
config = configparser.ConfigParser()
config.read(['Get_Data/Auth/config.cfg', 'config.dev.cfg'])
#Use the process data under the liner 'azure' in the file as the azure setting
azure_settings = config['azure']
headers = ''
headers_for_todo = ''

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
        global headers, headers_for_todo #Globalized headers so it can be used outside of the class 
        
        
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
        
        headers_for_todo = {
            'Authorization': f'Bearer {access_token.token}',
            'Content-Type': 'application/json'
        }
        
        return headers
    

#Returns the headers as a function so other file can access current headers
def get_headers():
    return headers

#Returns the header that is customized for to do tasks
def get_headers_for_todo():
    return headers_for_todo 

user = Account(azure_settings)

async def run_data():
    global headers 
    headers = await user.get_user_token()
