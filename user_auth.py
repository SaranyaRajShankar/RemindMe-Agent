from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
from database import save_user_token, get_user_token
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

def authenticate_user():
    """Authenticate a new user and save to database"""
    flow = InstalledAppFlow.from_client_secrets_file(
        "oauthCredentials.json", SCOPES
    )
    creds = flow.run_local_server(port=0)
    
    # Get user email
    service = build('oauth2', 'v2', credentials=creds)
    user_info = service.userinfo().get().execute()
    email = user_info.get('email', '')
    
    # Save user token to database
    save_user_token(email, creds)
    
    print(f"User connected: {email}")
    return email, creds