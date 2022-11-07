'''
Views specific to Zoho Books Integration
documentation: https://www.zoho.com/books/api/v3/
'''

import requests
from django.shortcuts import HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decouple import config
import secrets

@login_required
def connect_to_zoho_books(request):
    """
    Connect to Zoho Books API
    """
    # session = request.session 

    # store app state in session
    # session['app_state'] = secrets.token_urlsafe(16) # generate random string
    scope = "ZohoBooks.fullaccess.all"
    ZOHO_API_CLIENT_ID = config("ZOHO_API_CLIENT_ID", "")
    # state = session['app_state']
    # we can then use this state to verify the response
    # from Zoho Books by storing it in the db and comparing it to the state
    # returned by Zoho Books. For testing purposes, we'll just use a simple string.
    state = 'testing'
    response_type = "code"
    ZOHO_API_REDIRECT_URI = config(
        "ZOHO_API_REDIRECT_URI",
        "",
    )
    access_type = "offline"
    authorization_url = "https://accounts.zoho.com/oauth/v2/auth?"
    request_params = f"scope={scope}&client_id={ZOHO_API_CLIENT_ID}&state={state}&response_type={response_type}&redirect_uri={ZOHO_API_REDIRECT_URI}&access_type={access_type}"
    request_uri = authorization_url + request_params
    print(request_uri)
    print(state)
    return redirect(request_uri)

@csrf_exempt
@login_required
def zoho_books_callback(request):
    """
    Callback for Zoho Books API
    """
    state = request.GET.get("state")
    if not state == 'testing':
        return HttpResponse("Invalid state")
    else:
        try:
            code = request.GET["code"]
        except KeyError:
            code = None
        if not code:
            messages.error(
                request,
                f"There was an error connecting to zoho books. Please contact your Zoho admin if the problem persists.",
            )
            return redirect("integrations")
    query_params = {
                    'code': code,
                    'client_id': config("ZOHO_API_CLIENT_ID", ""),
                    'client_secret': config("ZOHO_API_CLIENT_SECRET", ""),
                    'redirect_uri': config("ZOHO_API_REDIRECT_URI", ""),
                    'grant_type': 'authorization_code',
                    }
    response = requests.post('https://accounts.zoho.com/oauth/v2/token', data=query_params)
    print(response.json())
    if response.status_code == 200:
        return store_token(request, response, service_name='zoho_books')
    else:
        error_message = (
            response.json().get("error", {}).get("error_text", "Unknown Error")
        )
        raise KeyError(f"HTTP.Error.{response.status_code}: {error_message}")

def store_token(request, response, service_name: str):
    """
    Store token in database
    """
    profile = request.user.profile
    profile.integration_info[service_name] = response.json()
    profile.save()
    messages.success(request, "Successfully connected to Zoho Books")
    return redirect("integrations")

def disconnect_from_zoho_books(request):
    """
    Disconnect from Zoho Books API
    """
    profile = request.user.profile
    profile.integration_info['zoho_books'] = {}
    profile.save()
    messages.success(request, "Successfully disconnected from Zoho Books")
    return redirect("integrations")