from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from credentials_context import get_user_credentials, set_user_credentials

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

def get_tomorrow_meetings():
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
    
    service = build('calendar', 'v3', credentials=creds)
    
    # Calculate tomorrow
    now = datetime.now()
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    day_after = tomorrow + timedelta(days=1)
    
    print(f"Searching for events between:")
    print(f"  Start: {tomorrow.isoformat()}")
    print(f"  End: {day_after.isoformat()}")
    
    try:
        # List accessible calendars
        calendar_list = service.calendarList().list().execute()
        print(f"\nAccessible calendars: {len(calendar_list.get('items', []))}")
        for cal in calendar_list.get('items', []):
            print(f"  - {cal['summary']} (ID: {cal['id']})")
        
        # Fetch events
        print("\nFetching events from primary calendar...")
        events_result = service.events().list(
            calendarId='primary',
            timeMin=tomorrow.isoformat() + 'Z',
            timeMax=day_after.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"Found {len(events)} events")
        
        if not events:
            print('\nNo events found for tomorrow.')
            return []
        
        print('\nTomorrow\'s meetings:')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            print(f"  - {summary} at {start}")
        
        return events
        
    except Exception as e:
        print(f"Error: {e}")
        return []