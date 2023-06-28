'''
Views specific to Zoho Books Integration

The OAuth dance is as follows:
    1. Redirect to Zoho Books OAuth page
    2. Zoho Books redirects back to our callback URL with a code
    3. Use the code to get an access token
    4. Store the access token in the database

Documentation: https://www.zoho.com/books/api/v3/
'''

# place imports at the top of the file
import requests # the requests library is used to make HTTP requests
# httpresponse is a django shortcut that returns an http response
# redirect is a django shortcut that redirects to a url
from django.shortcuts import HttpResponse, redirect
# login_required is a django shortcut that redirects to the login page if the user is not logged in
from django.contrib.auth.decorators import login_required
# messages is a django shortcut that allows us to display messages to the user
from django.contrib import messages
# config from the decouple library is used to get environment variables from the .env file
from decouple import config

# Create your views here.
# first view should be the one that redirects to the oauth page connect_to_zoho_books?
@login_required
def connect_to_zoho_books(request):
    """
    Connect to Zoho Books API. Your app must be registered with Zoho Books to use this.
    Then follow the documentation to build the request_url and redirect the user to it. 
    """
    # 1. Build the request_uri
    # 2. Redirect the user to the request_uri
    scope = "ZohoBooks.fullaccess.all"
    client_id = config("ZOHO_API_CLIENT_ID", "")
    state = "testing"
    response_type = "code"
    redirect_uri = config("ZOHO_API_REDIRECT_URI", "")
    access_type = "offline"
    params = f"scope={scope}&client_id={client_id}&state={state}&response_type={response_type}&redirect_uri={redirect_uri}&access_type={access_type}"
    request_uri = f"https://accounts.zoho.com/oauth/v2/auth?{params}"
    return redirect(request_uri)


@login_required
def zoho_books_callback(request):
    """
    Callback for Zoho Books API
    """
    # 1. Check the state parameter to make sure it matches the one you sent
    # 2. Get the code from the request
    # 3. Build the query parameters for the POST request based on the documentation
    # 4. Make the POST request to get the access token
    # 5. Store the access token in the database
    # 6. Redirect the user to the integrations page
    # TODO: Implement this
    state = request.GET.get("state", "")
    if state != "testing":
        return HttpResponse("Invalid state")
    else:
        code = request.GET.get("code", "")
        client_id = config("ZOHO_API_CLIENT_ID", "")
        client_secret = config("ZOHO_API_CLIENT_SECRET", "")
        redirect_uri = config("ZOHO_API_REDIRECT_URI", "")
        grant_type = "authorization_code"
        params = f"code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type={grant_type}"
        response = requests.post(f"https://accounts.zoho.com/oauth/v2/token?{params}")
        if response.status_code != 200:
            return HttpResponse("Error getting access token")
        else:
            store_token(request, response, "zoho_books")
    return redirect("integrations")
  
def store_token(request, response, service_name: str):
    """
    Store token in database
    """
    # 1. Get the access token from the response
    # 2. Store the access token in the database under the user's profile
    # in the integration_info field
    # 3. Redirect the user to the integrations page
    # 4. Display a success message to the user
    # TODO: Implement this
    messages.success(request, f"Successfully connected to {service_name}")
    return redirect("integrations")
   

def disconnect_from_zoho_books(request):
    """
    Disconnect from Zoho Books API
    """
    # 1. Delete the access token from the database
    # 2. Redirect the user to the integrations page
    # 3. Display a success message to the user
    # TODO: Implement this
    
    pass