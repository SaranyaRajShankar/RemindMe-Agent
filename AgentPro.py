import os
import uuid
import asyncio
from dotenv import load_dotenv

from getMeeting import get_tomorrow_meetings
from sendMail import send_email

from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import google_search, AgentTool, ToolContext

load_dotenv()

# -------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------
APP_NAME = "Meeting Reminder App"
USER_ID = "demo_user"

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# -------------------------------------------------------------------
# Meeting Reminder Agent
# -------------------------------------------------------------------
meeting_reminder_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="meeting_reminder_agent",
    instruction="""
You are a meeting reminder assistant.

When asked to remind someone about their meetings:
1. First, use the get_tomorrow_meetings tool to fetch tomorrow's calendar events.
2. Then, ALWAYS use the send_email tool to send a summary email with the meeting details.

RULES FOR send_email:
- Always pass a properly formatted 'body' parameter.
- Use list format:
    "Here are your meetings for tomorrow:\n\n* Meeting 1: 9:00 AM\n* Meeting 2: 2:00 PM"
- If no meetings → body="You have no meetings scheduled for tomorrow."
- Always include title and time.
- Use subject="Meeting Reminder for Tomorrow".
- Use to=None to auto-detect the recipient email.

You MUST always call send_email after getting the meetings, even if there are no meetings.
Always use both tools in sequence.
""",
    tools=[get_tomorrow_meetings, send_email],
)

# -------------------------------------------------------------------
# Session Service
# -------------------------------------------------------------------
session_service = InMemorySessionService()

# -------------------------------------------------------------------
# Run Session
# -------------------------------------------------------------------
async def run_session(
    runner_instance: Runner,
    user_queries: list[str] | str = None,
    session_name: str = "default",
):
    print(f"\n### Session: {session_name}")

    app_name = runner_instance.app_name

    # Load or create session
    try:
        session = await session_service.create_session(
            app_name=app_name,
            user_id=USER_ID,
            session_id=session_name
        )
    except Exception:
        session = await session_service.get_session(
            app_name=app_name,
            user_id=USER_ID,
            session_id=session_name
        )

    # Skip if no queries
    if not user_queries:
        print("No queries!")
        return

    # Normalize string → list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    # Iterate queries
    for query in user_queries:
        print(f"\nUser > {query}")

        query_obj = types.Content(
            role="user",
            parts=[types.Part(text=query)]
        )

        async for event in runner_instance.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=query_obj
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print("Agent >", text)

# -------------------------------------------------------------------
# Main Runner
# -------------------------------------------------------------------
async def main():
    runner = Runner(
        agent=meeting_reminder_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    await run_session(
        runner,
        user_queries="Get the user's meetings for tomorrow and send a summarized email to the user",
        session_name="demo_session"
    )

asyncio.run(main())
