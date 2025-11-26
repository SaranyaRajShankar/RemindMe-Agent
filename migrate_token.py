"""
Migrate existing token.json to the database
"""
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from database import save_user_token, init_db

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

def migrate_token():
    """Migrate token.json to database"""
    init_db()
    
    if not os.path.exists('token.json'):
        print("❌ token.json not found!")
        print("Run 'python -c \"from user_auth import authenticate_user; authenticate_user()\"' to add a user")
        return
    
    print("=" * 60)
    print("Migrating token.json to database...")
    print("=" * 60)
    
    try:
        # Load credentials from token.json
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # Get user email
        service = build('oauth2', 'v2', credentials=creds)
        user_info = service.userinfo().get().execute()
        email = user_info.get('email', '')
        
        if not email:
            print("❌ Could not determine user email from token")
            return
        
        print(f"\nFound user: {email}")
        
        # Save to database
        save_user_token(email, creds)
        
        print(f"✓ Successfully migrated {email} to database!")
        print(f"\nYou can now run 'python cron.py' to send reminders.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_token()