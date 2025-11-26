from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from credentials_context import get_user_credentials

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

def get_user_email(creds):
    """Get the authenticated user's email address"""
    try:
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        return user_info.get('email', '')
    except Exception as e:
        print(f"Error getting user email: {e}")
        return None

def send_email(to=None, subject="Meeting Reminder", body=""):
    # Try to get credentials from context first
    creds = get_user_credentials()
    
    # If no context credentials, fall back to token.json (for single-user mode)
    if not creds:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, let user log in (only for single-user mode)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/AI learnings/Meeting Reminder Agent/oauthCredentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run (single-user mode only)
        if not get_user_credentials():  # Only save if not using context
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
    
    # If no recipient specified, use the authenticated user's email
    if not to:
        to = get_user_email(creds)
        if not to:
            raise ValueError("Could not determine recipient email address")
    
    # Authenticate Gmail service
    service = build('gmail', 'v1', credentials=creds)
    
    # Create message
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    
    # Encode and send
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}
    
    service.users().messages().send(userId='me', body=body).execute()
    print(f"Email sent successfully to {to}")