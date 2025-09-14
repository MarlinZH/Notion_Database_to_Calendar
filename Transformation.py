import os
import logging
from notion_client import Client
from datetime import datetime, timedelta, timezone

# ----------------- Setup -----------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
TASKS_DB_ID = os.getenv("TASKS_DB_ID")          # Source tasks DB
CALENDAR_DB_ID = os.getenv("CALENDAR_DB_ID")    # Target calendar DB

if not NOTION_TOKEN or not TASKS_DB_ID or not CALENDAR_DB_ID:
    raise ValueError("Missing environment variables. Please set NOTION_TOKEN, TASKS_DB_ID, CALENDAR_DB_ID.")

notion = Client(auth=NOTION_TOKEN)

days_of_week = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
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
    """Find the next occurrence of a given weekday."""
    days_ahead = target_weekday - base_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return base_date + timedelta(days=days_ahead)


def event_exists(original_task_id):
    """Check if an event for this task already exists in the calendar DB."""
    response = notion.databases.query(
        database_id=CALENDAR_DB_ID,
        filter={
            "property": "Original Task ID",
            "rich_text": {"equals": original_task_id}
        }
    )
    return len(response["results"]) > 0


# ----------------- Main Logic -----------------
def spread_tasks():
    today = datetime.now(timezone.utc)  # timezone-aware
    tasks = get_all_tasks(TASKS_DB_ID)

    for task in tasks:
        props = task.get("properties", {})
        task_id = task.get("id")

        # Extract safely
        try:
            task_name = props["Name"]["title"][0]["text"]["content"]
            time_slot = props["Time Slot"]["rich_text"][0]["text"]["content"]
            days = [d["name"] for d in props["Days"]["multi_select"]]
        except (KeyError, IndexError) as e:
            logging.warning(f"Skipping task {task_id}: missing required property ({e})")
            continue

        # Skip if already in calendar
        if event_exists(task_id):
            logging.info(f"Skipping {task_name}: already scheduled.")
            continue

        # Process each day
        for day in days:
            if day not in days_of_week:
                logging.warning(f"Unknown day '{day}' for task {task_name}, skipping.")
                continue

            weekday_index = days_of_week[day]
            target_date = get_next_weekday(today, weekday_index)

            try:
                hour, minute = map(int, time_slot.split(":"))
            except ValueError:
                logging.warning(f"Invalid time format '{time_slot}' for task {task_name}, skipping.")
                continue

            task_datetime = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Create calendar entry
            try:
                notion.pages.create(
                    parent={"database_id": CALENDAR_DB_ID},
                    properties={
                        "Name": {"title": [{"text": {"content": task_name}}]},
                        "Date": {"date": {"start": task_datetime.isoformat()}},
                        "Original Task ID": {"rich_text": [{"text": {"content": task_id}}]}  # For deduplication
                    }
                )
                logging.info(f"Created calendar event for {task_name} on {task_datetime}")
            except Exception as e:
                logging.error(f"Failed to create event for {task_name}: {e}")


# ----------------- Run -----------------
if __name__ == "__main__":
    spread_tasks()
