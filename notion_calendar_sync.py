# #!/usr/bin/env python3
# """
# Notion -> Google Calendar one-way sync.

# Features:
# - Reads pages from a Notion database.
# - Converts Notion Date properties into Google Calendar event payloads.
# - Handles both all-day and datetime events using datetime + dateutil.parser.
# - Creates events in Google Calendar, or updates existing ones if a 'Google Event ID'
#   property exists on the Notion page.
#   - Writes the created/updated event ID back to Notion.

#   Environment variables (.env):
#     NOTION_TOKEN=secret_...
#       NOTION_DATABASE_ID=...
#         GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/service-account.json
#           GOOGLE_CALENDAR_ID=primary
#             TIMEZONE=America/New_York
#             """

import os
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from dotenv import load_dotenv
from notion_client import Client as NotionClient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser as date_parser

# Load env
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")   
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # path to JSON file
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", 'primary')    # default to primary calendar
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")

# Safety: dry-run default True
DRY_RUN = True

# Notion property names (adjust if different)
NOTION_TITLE_PROP = "Name"              # title property
NOTION_DATE_PROP = "Date"           # date property
NOTION_EVENT_ID_PROP = "Google Event ID"  # text/rich_text property

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("notion_to_calendar")


# --- Clients ---
def build_notion_client() -> NotionClient:
    if not NOTION_TOKEN:
        raise ValueError("NOTION_TOKEN is not set.")
    return NotionClient(auth=NOTION_TOKEN)


def build_calendar_service():
    if not GOOGLE_SERVICE_ACCOUNT_FILE:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE is not set.")
        scopes = ["https://www.googleapis.com/auth/calendar"]
        creds = service_account.Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_FILE, scopes=scopes)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


# --- Notion helpers ---
def query_notion_database(notion: NotionClient, database_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
    pages = []
    start_cursor = None
    while True:
        response = notion.databases.query(
          **{"database_id": database_id, "page_size": page_size, **({"start_cursor": start_cursor} if start_cursor else {})}

    pages.extend(response.get("results", []))
    if not response.get("has_more"):
    break
    start_cursor = response.get("next_cursor")
    logger.info("Queried Notion DB: %d pages found", len(pages))
    return pages


    def extract_title(page: Dict[str, Any]) -> str:
    props = page.get("properties", {})
    title_prop = props.get(NOTION_TITLE_PROP)
    if not title_prop:
    return "(no title property)"
    for rich in title_prop.get("title", []):
    if "plain_text" in rich and rich["plain_text"]:
    return rich["plain_text"]
    if "text" in rich and "content" in rich["text"]:
    return rich["text"]["content"]
    return "(untitled)"


    def extract_date_property(page: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    props = page.get("properties", {})
    date_prop = props.get(NOTION_DATE_PROP)
    if not date_prop:
    return None
    return date_prop.get("date")


    def get_page_event_id(page: Dict[str, Any]) -> Optional[str]:
    props = page.get("properties", {})
    ev_prop = props.get(NOTION_EVENT_ID_PROP)
    if not ev_prop:
    return None
    if "rich_text" in ev_prop and ev_prop["rich_text"]:
    return ev_prop["rich_text"][0].get("plain_text")
    if "title" in ev_prop and ev_prop["title"]:
    return ev_prop["title"][0].get("plain_text")
    return None


    def notion_patch_event_id(notion: NotionClient, page_id: str, event_id: str) -> None:
    try:
    notion.pages.update(
    page_id=page_id,
    properties={NOTION_EVENT_ID_PROP: {"rich_text": [{"text": {"content": event_id}}]}}
    )
    logger.info("Wrote event id to Notion page %s: %s", page_id, event_id)
    except Exception as e:
    logger.exception("Failed to write event id to Notion page %s: %s", page_id, e)


    # --- Calendar helpers ---
    def build_event_payload(title: str, date_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a Google Calendar event payload from a Notion date object.
    Uses datetime + dateutil.parser for robustness.
    """
    start_str = date_obj.get("start")
    end_str = date_obj.get("end")

    if not start_str:
    raise ValueError("Date object missing 'start'.")

    is_all_day = "T" not in start_str

    if is_all_day:
    start_date = date_parser.parse(start_str).date()
    end_date = date_parser.parse(end_str).date() if end_str else start_date + timedelta(days=1)
    return {
    "summary": title,
    "start": {"date": start_date.isoformat()},
    "end": {"date": end_date.isoformat()},
    }
    else:
    start_dt = date_parser.parse(start_str)
    end_dt = date_parser.parse(end_str) if end_str else start_dt + timedelta(hours=1)
    return {
    "summary": title,
    "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
    "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE},
    }


    def create_calendar_event(service, calendar_id: str, event_payload: Dict[str, Any]) -> Dict[str, Any]:
    if DRY_RUN:
    logger.info("[DRY RUN] Would create event: %s", event_payload)
    return {"id": "dry-run-event-id", **event_payload}
    created = service.events().insert(calendarId=calendar_id, body=event_payload).execute()
    logger.info("Created event: %s (%s)", created.get("summary"), created.get("id"))
    return created


    def update_calendar_event(service, calendar_id: str, event_id: str, event_payload: Dict[str, Any]) -> Dict[str, Any]:
    if DRY_RUN:
    logger.info("[DRY RUN] Would update event %s: %s", event_id, event_payload)
    return {"id": event_id, **event_payload}
    updated = service.events().update(calendarId=calendar_id, eventId=event_id, body=event_payload).execute()
    logger.info("Updated event: %s (%s)", updated.get("summary"), updated.get("id"))
    return updated


    # --- Sync ---
    def sync_page(notion: NotionClient, service, calendar_id: str, page: Dict[str, Any]) -> None:
    page_id = page.get("id")
    title = extract_title(page)
    date_obj = extract_date_property(page)
    if not date_obj:
    # Try to get Day of the Week and Time Slot
    props = page.get("properties", {})
    day_prop = props.get("Day of the Week", {})
    time_prop = props.get("Time Slot", {})
    days = [d["name"] for d in day_prop.get("multi_select", [])]
    time_slot = None
    if "rich_text" in time_prop and time_prop["rich_text"]:
    time_slot = time_prop["rich_text"][0]["plain_text"] if "plain_text" in time_prop["rich_text"][0] else time_prop["rich_text"][0]["text"]["content"]
    if not days or not time_slot:
    logger.info(f"Skipping page {page_id} (no date property and missing Day of the Week or Time Slot)")
    return
    # Map day names to weekday numbers
    day_map = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
    }
    # Parse time_slot (expects HHMM)
    try:
    if len(time_slot) == 4 and time_slot.isdigit():
    hour = int(time_slot[:2])
    minute = int(time_slot[2:])
    else:
    raise ValueError("Expected HHMM format, e.g., 0600 or 1345")
    except Exception as e:
    logger.warning(f"Invalid time format '{time_slot}' for page {page_id}, skipping. ({e})")
    return
    # Generate dates for each weekday until end of year
    today = datetime.now()
    end_date = datetime(today.year, 12, 31)
    for day in days:
    # Remove any prefix like '1-Monday'
    day_name = day.split('-')[-1] if '-' in day else day
    weekday_num = day_map.get(day_name)
    if weekday_num is None:
    logger.warning(f"Unknown day '{day}' for page {page_id}, skipping.")
    continue
    # Find first occurrence
    current = today
    while current.weekday() != weekday_num:
    current += timedelta(days=1)
    # Loop through all occurrences until end of year
    while current <= end_date:
    event_start = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
    event_end = event_start + timedelta(hours=1)
    payload = {
    "summary": title,
    "start": {"dateTime": event_start.isoformat(), "timeZone": TIMEZONE},
    "end": {"dateTime": event_end.isoformat(), "timeZone": TIMEZONE},
    }
    try:
    created = create_calendar_event(service, calendar_id, payload)
    if created and created.get("id") and not DRY_RUN:
    notion_patch_event_id(notion, page_id, created.get("id"))
    except Exception as e:
    logger.error(f"Failed to create calendar event for {title} on {event_start.date()}: {e}")
    current += timedelta(days=7)
    return
    existing_event_id = get_page_event_id(page)
    try:
    if existing_event_id:
    try:
    updated = update_calendar_event(service, calendar_id, existing_event_id, payload)
    if not DRY_RUN:
    notion_patch_event_id(notion, page_id, updated.get("id"))
    except HttpError as e:
    if "404" in str(e):
    created = create_calendar_event(service, calendar_id, payload)
    if not DRY_RUN:
    notion_patch_event_id(notion, page_id, created.get("id"))
    else:
    raise
    else:
    created = create_calendar_event(service, calendar_id, payload)
    if created and created.get("id") and not DRY_RUN:
    notion_patch_event_id(notion, page_id, created.get("id"))
    except Exception as e:
    logger.exception("Error syncing page %s: %s", page_id, e)



    def run_sync(dry_run: bool = True, max_pages: Optional[int] = None):
    global DRY_RUN
    DRY_RUN = dry_run
    notion = build_notion_client()
    service = build_calendar_service()
    pages = query_notion_database(notion, NOTION_DB_ID)
    if max_pages:
    pages = pages[:max_pages]
    logger.info("Processing %d pages", len(pages))

    for i, page in enumerate(pages, start=1):
    logger.info("Processing page %d/%d", i, len(pages))
    try:
    sync_page(notion, service, GOOGLE_CALENDAR_ID, page)
    time.sleep(0.2)  # throttle
    except Exception as e:
    logger.exception("Unhandled error syncing page %s: %s", page.get("id"), e)


    if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync Notion DB to Google Calendar")
    parser.add_argument("--no-dry-run", action="store_true", help="Disable dry-run and perform writes")
    parser.add_argument("--max-pages", type=int, default=None, help="Process only N pages (for testing)")
    args = parser.parse_args()

    logger.info("Starting Notion -> Google Calendar sync (dry-run=%s)", not args.no_dry_run)
    run_sync(dry_run=not args.no_dry_run, max_pages=args.max_pages)
    logger.info("Done.")
