import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from notion_client import Client
from googleapiclient.discovery import build
from google.oauth2 import service_account

# ----------------- Setup -----------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

load_dotenv()

# Notion setup
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
TASKS_DB_ID = os.getenv("NOTION_DATABASE_ID")   

notion = Client(auth=NOTION_TOKEN)

# Google Calendar setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # path to JSON file
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", 'primary')    # default to primary calendar

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
calendar_service = build('calendar', 'v3', credentials=credentials)

# Days mapping
days_of_week = {
    "1-Monday": 0,
    "2-Tuesday": 1,
    "3-Wednesday": 2,
    "4-Thursday": 3,
    "5-Friday": 4,
    "6-Saturday": 5,
    "Sunday": 6
}

# ----------------- Helpers -----------------
def get_all_tasks(db_id):
    """Fetch all tasks from a Notion database, handling pagination."""
    results = []
    next_cursor = None
    while True:
        response = notion.databases.query(database_id=db_id, start_cursor=next_cursor)
        results.extend(response["results"])
        if not response.get("has_more"):
            break
        next_cursor = response.get("next_cursor")
    return results

def get_next_weekday(base_date, target_weekday):
    days_ahead = target_weekday - base_date.weekday()
    print(f"Days ahead: {days_ahead}")
    if days_ahead <= 0:
        days_ahead += 7
        print(f"Adjusted days ahead: {days_ahead}")
    return base_date + timedelta(days=days_ahead)

def event_exists_in_notion(task_id):
    """Check if a Google Calendar event has already been linked in Notion."""
    task = notion.pages.retrieve(task_id)
    props = task.get("properties", {})
    return "Google Event ID" in props and props["Google Event ID"].get("rich_text")

def create_google_event(task_name, task_datetime):
    """Create a Google Calendar event and return the event ID."""
    event = {
        'summary': task_name,
        'start': {'dateTime': task_datetime.isoformat(), 'timeZone': 'America/New_York'},
        'end': {'dateTime': (task_datetime + timedelta(hours=1)).isoformat(), 'timeZone': 'America/New_York'},
       'RRULE': {'freq': 'WEEKLY', 'byweekday': [days_of_week[day]]}
    }
    created_event = calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created_event['id'], created_event.get('htmlLink')

# ----------------- Main Logic -----------------
def push_tasks_to_calendar():
    today = datetime.now(timezone.utc)
    tasks = get_all_tasks(TASKS_DB_ID)

    for task in tasks:
        task_id = task["id"]
        props = task.get("properties", {})
        print(props["Tasks"]["title"][0]["text"]["content"])
        # print(props)
        # Skip if already linked to Google Calendar
        if event_exists_in_notion(task_id):
            logging.info(f"Skipping {task_id}: already linked to calendar.")
            continue

        try:
            task_name = props["Tasks"]["title"][0]["text"]["content"]
            time_slot = props["Time Slot"]["rich_text"][0]["text"]["content"]
            days = [d["name"] for d in props["Day of the Week"]["multi_select"]]
            print("FINISIHED PROPERTIES")
        except (KeyError, IndexError) as e:
            logging.warning(f"Skipping {task_id}: missing required property ({e})")
            continue

        for day in days:
            if day not in days_of_week:
                logging.warning(f"Unknown day '{day}' for task {task_name}, skipping.")
                continue

            weekday_index = days_of_week[day]
            target_date = get_next_weekday(today, weekday_index)

            

            try:
                if len(time_slot) == 4 and time_slot.isdigit():
                    hour = int(time_slot[:2])
                    minute = int(time_slot[2:])
                else:
                    raise ValueError("Expected HHMM format, e.g., 0600 or 1345")
            except ValueError as e:
                logging.warning(f"Invalid time format '{time_slot}' for task {task_name}, skipping. ({e})")
                continue

            task_datetime = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Create Google Calendar event
            try:
                event_id, event_link = create_google_event(task_name, task_datetime)
                logging.info(f"Created Google Calendar event: {event_link}")

                # Store the Google Event ID in Notion for deduplication
                notion.pages.update(
                    page_id=task_id,
                    properties={
                        "Google Event ID": {
                            "rich_text": [{"text": {"content": event_id}}]
                        }
                    }
                )
            except Exception as e:
                logging.error(f"Failed to create calendar event for {task_name}: {e}")

# ----------------- Run -----------------
if __name__ == "__main__":
    push_tasks_to_calendar()
