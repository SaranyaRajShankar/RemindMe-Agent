import contextvars
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json

# Context variable for credentials (works with asyncio)
_user_credentials: contextvars.ContextVar[Credentials | None] = contextvars.ContextVar(
    'user_credentials', default=None
)

def set_user_credentials(creds):
    """Set credentials for the current async task/user"""
    _user_credentials.set(creds)

def get_user_credentials():
    """Get credentials for the current async task/user"""
    return _user_credentials.get()

def get_credentials_from_db(token_json_str):
    """Load credentials from database token JSON string"""
    from google.oauth2.credentials import Credentials
    token_data = json.loads(token_json_str)
    creds = Credentials.from_authorized_user_info(token_data)
    
    # Refresh if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    return creds