#!/usr/bin/env python3
"""
Notion -> Google Calendar one-way sync.

Features:
- Reads pages from a Notion database.
- Converts Notion Date properties into Google Calendar event payloads.
- Handles both all-day and datetime events using datetime + dateutil.parser.
- Creates events in Google Calendar, or updates existing ones if a 'Google Event ID'
  property exists on the Notion page.
- Writes the created/updated event ID back to Notion.
- Supports Duration field for custom event lengths
- Implements Frequency-based recurring events (Daily, Weekly, Bi-Weekly, Monthly, Bi-Monthly)
- Supports Priority-based color coding in Google Calendar

Environment variables (.env):
  NOTION_API_KEY=secret_...
  NOTION_DATABASE_ID=...
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
  GOOGLE_CALENDAR_ID=primary
  TIMEZONE=America/New_York
"""

import os
import logging
import time
import argparse
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv
from notion_client import Client as NotionClient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

# Load environment variables
load_dotenv()

# Environment configuration
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", 'primary')
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")

# Safety: dry-run default True
DRY_RUN = True

# Notion property names (updated to match your database)
NOTION_TITLE_PROP = "Tasks"  # Updated from "Name" to "Tasks"
NOTION_DATE_PROP = "Date"
NOTION_EVENT_ID_PROP = "Google Event ID"
NOTION_DAY_PROP = "Day of the Week"
NOTION_TIME_PROP = "Time Slot"
NOTION_DURATION_PROP = "Duration"  # New: Duration in minutes
NOTION_PRIORITY_PROP = "Priority"  # New: For color coding
NOTION_FREQUENCY_PROP = "Frequency"  # New: For recurrence pattern

# Weekday mapping (Monday=0, Sunday=6)
DAY_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

# Frequency to days mapping
FREQUENCY_MAP = {
    "Daily": 1,
    "Weekly": 7,
    "Bi-Weekly": 14,
    "Monthly": None,  # Uses relativedelta
    "Bi-Monthly": None,  # Uses relativedelta
}

# Priority to Google Calendar color ID mapping
# https://developers.google.com/calendar/api/v3/reference/colors
PRIORITY_COLORS = {
    "High": "11",      # Red
    "Medium": "5",     # Yellow/Banana
    "Low": "10",       # Green/Basil
}

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("notion_to_calendar")


def validate_environment() -> None:
    """Validate that all required environment variables are set."""
    required_vars = {
        "NOTION_API_KEY": NOTION_TOKEN,
        "NOTION_DATABASE_ID": NOTION_DB_ID,
        "GOOGLE_APPLICATION_CREDENTIALS": GOOGLE_SERVICE_ACCOUNT_FILE,
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE):
        error_msg = f"Google service account file not found: {GOOGLE_SERVICE_ACCOUNT_FILE}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logger.info("Environment validation passed")


def build_notion_client() -> NotionClient:
    """Build and return a Notion client."""
    return NotionClient(auth=NOTION_TOKEN)


def build_calendar_service():
    """Build and return a Google Calendar service."""
    scopes = ["https://www.googleapis.com/auth/calendar"]
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def query_notion_database(
    notion: NotionClient, database_id: str, page_size: int = 100
) -> List[Dict[str, Any]]:
    """Query Notion database and return all pages with pagination support."""
    pages = []
    start_cursor = None
    
    while True:
        query_params = {"database_id": database_id, "page_size": page_size}
        if start_cursor:
            query_params["start_cursor"] = start_cursor
        
        response = notion.databases.query(**query_params)
        pages.extend(response.get("results", []))
        
        if not response.get("has_more"):
            break
        start_cursor = response.get("next_cursor")
    
    logger.info(f"Queried Notion DB: {len(pages)} pages found")
    return pages


def extract_title(page: Dict[str, Any]) -> str:
    """Extract title from Notion page."""
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
    """Extract date property from Notion page."""
    props = page.get("properties", {})
    date_prop = props.get(NOTION_DATE_PROP)
    
    if not date_prop:
        return None
    
    return date_prop.get("date")


def extract_days_and_time(page: Dict[str, Any]) -> Tuple[List[str], Optional[str]]:
    """Extract day of week and time slot from Notion page."""
    props = page.get("properties", {})
    
    # Extract days
    day_prop = props.get(NOTION_DAY_PROP, {})
    days = [d["name"] for d in day_prop.get("multi_select", [])]
    
    # Extract time slot
    time_prop = props.get(NOTION_TIME_PROP, {})
    time_slot = None
    
    if "rich_text" in time_prop and time_prop["rich_text"]:
        time_text = time_prop["rich_text"][0]
        time_slot = time_text.get("plain_text") or time_text.get("text", {}).get("content")
    
    return days, time_slot


def extract_duration(page: Dict[str, Any]) -> float:
    """Extract duration in hours from Notion page (Duration field is in minutes)."""
    props = page.get("properties", {})
    duration_prop = props.get(NOTION_DURATION_PROP)
    
    if duration_prop and "number" in duration_prop and duration_prop["number"] is not None:
        minutes = duration_prop["number"]
        hours = minutes / 60.0
        logger.debug(f"Duration: {minutes} minutes = {hours} hours")
        return hours
    
    # Default to 1 hour if no duration specified
    return 1.0


def extract_priority(page: Dict[str, Any]) -> Optional[str]:
    """Extract priority from Notion page."""
    props = page.get("properties", {})
    priority_prop = props.get(NOTION_PRIORITY_PROP, {})
    
    if "select" in priority_prop and priority_prop["select"]:
        return priority_prop["select"]["name"]
    
    return None


def extract_frequency(page: Dict[str, Any]) -> Optional[str]:
    """Extract frequency from Notion page."""
    props = page.get("properties", {})
    frequency_prop = props.get(NOTION_FREQUENCY_PROP, {})
    
    if "select" in frequency_prop and frequency_prop["select"]:
        return frequency_prop["select"]["name"]
    
    return None


def get_event_color(priority: Optional[str]) -> Optional[str]:
    """Get Google Calendar color ID based on priority."""
    if priority and priority in PRIORITY_COLORS:
        return PRIORITY_COLORS[priority]
    return None


def parse_time_slot(time_slot: str) -> Tuple[int, int]:
    """Parse time slot string (HHMM format) into hour and minute."""
    if len(time_slot) != 4 or not time_slot.isdigit():
        raise ValueError(f"Expected HHMM format (e.g., 0600), got: {time_slot}")
    
    hour = int(time_slot[:2])
    minute = int(time_slot[2:])
    
    if not (0 <= hour <= 23) or not (0 <= minute <= 59):
        raise ValueError(f"Invalid time: {hour:02d}:{minute:02d}")
    
    return hour, minute


def get_page_event_id(page: Dict[str, Any]) -> Optional[str]:
    """Get existing Google Calendar event ID from Notion page."""
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
    """Write Google Calendar event ID back to Notion page."""
    try:
        notion.pages.update(
            page_id=page_id,
            properties={
                NOTION_EVENT_ID_PROP: {"rich_text": [{"text": {"content": event_id}}]}
            }
        )
        logger.info(f"Wrote event ID to Notion page {page_id}: {event_id}")
    except Exception as e:
        logger.error(f"Failed to write event ID to Notion page {page_id}: {e}")


def build_event_payload(
    title: str, 
    date_obj: Dict[str, Any], 
    color_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build a Google Calendar event payload from a Notion date object.
    Handles both all-day and datetime events.
    """
    start_str = date_obj.get("start")
    end_str = date_obj.get("end")
    
    if not start_str:
        raise ValueError("Date object missing 'start'.")
    
    is_all_day = "T" not in start_str
    
    payload = {}
    
    if is_all_day:
        start_date = date_parser.parse(start_str).date()
        end_date = (
            date_parser.parse(end_str).date() if end_str 
            else start_date + timedelta(days=1)
        )
        payload = {
            "summary": title,
            "start": {"date": start_date.isoformat()},
            "end": {"date": end_date.isoformat()},
        }
    else:
        start_dt = date_parser.parse(start_str)
        end_dt = (
            date_parser.parse(end_str) if end_str 
            else start_dt + timedelta(hours=1)
        )
        payload = {
            "summary": title,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE},
        }
    
    # Add color if priority is set
    if color_id:
        payload["colorId"] = color_id
    
    return payload


def build_event_payload_from_time(
    title: str, 
    event_datetime: datetime, 
    duration_hours: float = 1.0,
    color_id: Optional[str] = None
) -> Dict[str, Any]:
    """Build event payload from a datetime and duration."""
    event_end = event_datetime + timedelta(hours=duration_hours)
    
    payload = {
        "summary": title,
        "start": {"dateTime": event_datetime.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": event_end.isoformat(), "timeZone": TIMEZONE},
    }
    
    # Add color if priority is set
    if color_id:
        payload["colorId"] = color_id
    
    return payload


def create_calendar_event(
    service, calendar_id: str, event_payload: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new Google Calendar event."""
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would create event: {event_payload['summary']}")
        return {"id": "dry-run-event-id", **event_payload}
    
    created = service.events().insert(calendarId=calendar_id, body=event_payload).execute()
    logger.info(f"Created event: {created.get('summary')} ({created.get('id')})")
    return created


def update_calendar_event(
    service, calendar_id: str, event_id: str, event_payload: Dict[str, Any]
) -> Dict[str, Any]:
    """Update an existing Google Calendar event."""
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would update event {event_id}: {event_payload['summary']}")
        return {"id": event_id, **event_payload}
    
    updated = service.events().update(
        calendarId=calendar_id, eventId=event_id, body=event_payload
    ).execute()
    logger.info(f"Updated event: {updated.get('summary')} ({updated.get('id')})")
    return updated


def sync_page_with_date(
    notion: NotionClient,
    service,
    calendar_id: str,
    page: Dict[str, Any],
    title: str,
    date_obj: Dict[str, Any],
    priority: Optional[str] = None
) -> None:
    """Sync a page that has a specific date."""
    page_id = page.get("id")
    existing_event_id = get_page_event_id(page)
    color_id = get_event_color(priority)
    
    try:
        payload = build_event_payload(title, date_obj, color_id)
        
        if existing_event_id:
            # Try to update existing event
            try:
                updated = update_calendar_event(service, calendar_id, existing_event_id, payload)
                if not DRY_RUN:
                    notion_patch_event_id(notion, page_id, updated.get("id"))
            except HttpError as e:
                if "404" in str(e):
                    # Event no longer exists, create new one
                    logger.warning(f"Event {existing_event_id} not found, creating new event")
                    created = create_calendar_event(service, calendar_id, payload)
                    if not DRY_RUN:
                        notion_patch_event_id(notion, page_id, created.get("id"))
                else:
                    raise
        else:
            # Create new event
            created = create_calendar_event(service, calendar_id, payload)
            if not DRY_RUN:
                notion_patch_event_id(notion, page_id, created.get("id"))
    
    except Exception as e:
        logger.error(f"Error syncing page {page_id} with date: {e}")


def get_next_occurrence(
    current: datetime, 
    frequency: str, 
    weekday_num: Optional[int] = None
) -> datetime:
    """Get the next occurrence based on frequency."""
    if frequency == "Daily":
        return current + timedelta(days=1)
    elif frequency == "Weekly":
        return current + timedelta(days=7)
    elif frequency == "Bi-Weekly":
        return current + timedelta(days=14)
    elif frequency == "Monthly":
        return current + relativedelta(months=1)
    elif frequency == "Bi-Monthly":
        return current + relativedelta(months=2)
    else:
        # Default to weekly
        return current + timedelta(days=7)


def sync_page_with_recurring(
    notion: NotionClient,
    service,
    calendar_id: str,
    page: Dict[str, Any],
    title: str,
    days: List[str],
    time_slot: str,
    duration_hours: float = 1.0,
    priority: Optional[str] = None,
    frequency: Optional[str] = "Weekly"
) -> None:
    """Sync a page that has recurring day/time schedule with custom frequency."""
    page_id = page.get("id")
    color_id = get_event_color(priority)
    
    try:
        hour, minute = parse_time_slot(time_slot)
    except ValueError as e:
        logger.warning(f"Invalid time format '{time_slot}' for page {page_id}: {e}")
        return
    
    today = datetime.now()
    end_date = datetime(today.year, 12, 31)
    events_created = 0
    
    # If frequency is Daily, ignore the days list and create events every day
    if frequency == "Daily":
        current = today
        while current <= end_date:
            event_datetime = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
            payload = build_event_payload_from_time(title, event_datetime, duration_hours, color_id)
            
            try:
                created = create_calendar_event(service, calendar_id, payload)
                events_created += 1
                
                # Only write first event ID back to Notion
                if events_created == 1 and created and created.get("id") and not DRY_RUN:
                    notion_patch_event_id(notion, page_id, created.get("id"))
            
            except Exception as e:
                logger.error(f"Failed to create event for {title} on {event_datetime.date()}: {e}")
            
            current = get_next_occurrence(current, frequency)
    else:
        # For non-daily frequencies, iterate through specified days of week
        for day in days:
            # Remove any prefix like '1-Monday'
            day_name = day.split('-')[-1] if '-' in day else day
            weekday_num = DAY_MAP.get(day_name)
            
            if weekday_num is None:
                logger.warning(f"Unknown day '{day}' for page {page_id}, skipping.")
                continue
            
            # Find first occurrence of this weekday
            current = today
            while current.weekday() != weekday_num:
                current += timedelta(days=1)
            
            # Create events for all occurrences until end of year
            while current <= end_date:
                event_datetime = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
                payload = build_event_payload_from_time(title, event_datetime, duration_hours, color_id)
                
                try:
                    created = create_calendar_event(service, calendar_id, payload)
                    events_created += 1
                    
                    # Only write first event ID back to Notion
                    if events_created == 1 and created and created.get("id") and not DRY_RUN:
                        notion_patch_event_id(notion, page_id, created.get("id"))
                
                except Exception as e:
                    logger.error(f"Failed to create event for {title} on {event_datetime.date()}: {e}")
                
                current = get_next_occurrence(current, frequency or "Weekly", weekday_num)
    
    logger.info(f"Created {events_created} recurring events ({frequency or 'Weekly'}) for page {page_id}")


def sync_page(
    notion: NotionClient, service, calendar_id: str, page: Dict[str, Any]
) -> None:
    """Sync a single Notion page to Google Calendar."""
    page_id = page.get("id")
    title = extract_title(page)
    
    if not title or title in ["(no title property)", "(untitled)"]:
        logger.warning(f"Skipping page {page_id}: no valid title")
        return
    
    # Extract additional properties
    priority = extract_priority(page)
    duration_hours = extract_duration(page)
    frequency = extract_frequency(page)
    
    # Check if page has a specific date
    date_obj = extract_date_property(page)
    
    if date_obj:
        # Single event with specific date
        sync_page_with_date(notion, service, calendar_id, page, title, date_obj, priority)
    else:
        # Recurring events based on day/time/frequency
        days, time_slot = extract_days_and_time(page)
        
        if not days or not time_slot:
            logger.info(
                f"Skipping page {page_id}: no date property and missing Day of the Week or Time Slot"
            )
            return
        
        sync_page_with_recurring(
            notion, service, calendar_id, page, title, days, time_slot, 
            duration_hours, priority, frequency
        )


def run_sync(dry_run: bool = True, max_pages: Optional[int] = None) -> None:
    """Run the sync process."""
    global DRY_RUN
    DRY_RUN = dry_run
    
    # Validate environment
    validate_environment()
    
    # Build clients
    notion = build_notion_client()
    service = build_calendar_service()
    
    # Query database
    pages = query_notion_database(notion, NOTION_DB_ID)
    
    if max_pages:
        pages = pages[:max_pages]
        logger.info(f"Limiting to {max_pages} pages for testing")
    
    logger.info(f"Processing {len(pages)} pages")
    
    # Sync each page
    success_count = 0
    error_count = 0
    
    for i, page in enumerate(pages, start=1):
        logger.info(f"Processing page {i}/{len(pages)}")
        try:
            sync_page(notion, service, GOOGLE_CALENDAR_ID, page)
            success_count += 1
            time.sleep(0.2)  # Rate limiting
        except Exception as e:
            error_count += 1
            logger.exception(f"Unhandled error syncing page {page.get('id')}: {e}")
    
    logger.info(f"\n{'='*50}")
    logger.info(f"Sync completed!")
    logger.info(f"Successfully processed: {success_count}")
    logger.info(f"Errors: {error_count}")
    logger.info(f"{'='*50}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sync Notion DB to Google Calendar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run mode (default, no changes made):
  python notion_calendar_sync.py
  
  # Actual sync (writes to calendar):
  python notion_calendar_sync.py --no-dry-run
  
  # Test with limited pages:
  python notion_calendar_sync.py --max-pages 5
        """
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Disable dry-run and perform actual writes to Google Calendar"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Process only N pages (for testing purposes)"
    )
    args = parser.parse_args()
    
    mode = "LIVE" if args.no_dry_run else "DRY-RUN"
    logger.info(f"Starting Notion -> Google Calendar sync (mode: {mode})")
    
    try:
        run_sync(dry_run=not args.no_dry_run, max_pages=args.max_pages)
    except KeyboardInterrupt:
        logger.info("\nSync interrupted by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        exit(1)
