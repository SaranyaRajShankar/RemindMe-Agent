import threading
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

# Thread-local storage for credentials
_thread_local = threading.local()

def set_user_credentials(creds):
    """Set credentials for the current thread/user"""
    _thread_local.creds = creds

def get_user_credentials():
    """Get credentials for the current thread/user"""
    return getattr(_thread_local, 'creds', None)

def get_credentials_from_db(token_json_str):
    """Load credentials from database token JSON string"""
    from google.oauth2.credentials import Credentials
    token_data = json.loads(token_json_str)
    creds = Credentials.from_authorized_user_info(token_data)
    
    # Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds