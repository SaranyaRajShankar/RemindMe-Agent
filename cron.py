import asyncio
from AgentPro import run_session, session_service, meeting_reminder_agent
from google.adk.runners import Runner
from database import get_all_users, get_user_token, init_db
from credentials_context import set_user_credentials, get_credentials_from_db
from google.auth.transport.requests import Request

APP_NAME = "Meeting Reminder App"

async def run_agent_for_user(email, token_json):
    """Run the agent for a specific user"""
    print(f"\n{'='*60}")
    print(f"Running reminder for: {email}")
    print(f"{'='*60}")
    
    try:
        # Load credentials from database
        creds = get_credentials_from_db(token_json)
        
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            print(f"Refreshing expired token for {email}...")
            creds.refresh(Request())
            # Update database with refreshed token
            from database import save_user_token
            save_user_token(email, creds)
        
        # Set credentials in context for this user
        set_user_credentials(creds)
        
        runner = Runner(
            agent=meeting_reminder_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        
        query = (
            "Get the user's meetings for tomorrow and send a summarized email "
            "to the user from their own Gmail account."
        )
        
        await run_session(
            runner_instance=runner,
            user_queries=query,
            session_name=f"daily_run_{email}"
        )
        
        print(f"✓ Completed reminder for: {email}")
        
    except Exception as e:
        print(f"✗ Error processing {email}: {e}")
        import traceback
        traceback.print_exc()

async def run_daily_agent():
    """Run the agent for all users in the database"""
    # Ensure database is initialized
    init_db()
    
    users = get_all_users()
    
    if not users:
        print("No users found in database.")
        print("To add a user, run: python -c 'from user_auth import authenticate_user; authenticate_user()'")
        return
    
    print(f"\n{'='*60}")
    print(f"Processing {len(users)} user(s)...")
    print(f"{'='*60}\n")
    
    # Run for all users concurrently
    tasks = []
    for email, token_json in users:
        tasks.append(run_agent_for_user(email, token_json))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Check for errors
    errors = [r for r in results if isinstance(r, Exception)]
    if errors:
        print(f"\n⚠ {len(errors)} error(s) occurred during processing")
    
    print(f"\n{'='*60}")
    print("Daily agent run completed")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(run_daily_agent())