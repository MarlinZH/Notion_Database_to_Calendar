# API Documentation

This document describes the internal API of the Notion Database to Calendar sync tool.

## Core Functions

### Environment & Setup

#### `validate_environment() -> None`

Validates that all required environment variables are set and files exist.

**Raises:**
- `ValueError`: If required environment variables are missing
- `FileNotFoundError`: If Google service account file not found

**Example:**
```python
validate_environment()
# Raises error if .env is not configured correctly
```

---

#### `build_notion_client() -> NotionClient`

Creates and returns a Notion API client.

**Returns:**
- `NotionClient`: Authenticated Notion client

**Example:**
```python
notion = build_notion_client()
db = notion.databases.retrieve(database_id="...")
```

---

#### `build_calendar_service()`

Creates and returns a Google Calendar API service.

**Returns:**
- Google Calendar service object

**Example:**
```python
service = build_calendar_service()
events = service.events().list(calendarId='primary').execute()
```

---

### Data Extraction

#### `query_notion_database(notion, database_id, page_size=100) -> List[Dict]`

Queries a Notion database and returns all pages with pagination support.

**Parameters:**
- `notion` (NotionClient): Authenticated Notion client
- `database_id` (str): Notion database ID
- `page_size` (int, optional): Number of results per page (default: 100)

**Returns:**
- `List[Dict]`: List of page objects from Notion

**Example:**
```python
notion = build_notion_client()
pages = query_notion_database(notion, "abc123...")
print(f"Found {len(pages)} pages")
```

---

#### `extract_title(page) -> str`

Extracts the title from a Notion page.

**Parameters:**
- `page` (Dict): Notion page object

**Returns:**
- `str`: Title text, or "(no title property)"/"(untitled)" if missing

**Example:**
```python
title = extract_title(page)
print(f"Event: {title}")
```

---

#### `extract_date_property(page) -> Optional[Dict]`

Extracts the date property from a Notion page.

**Parameters:**
- `page` (Dict): Notion page object

**Returns:**
- `Dict` or `None`: Date object with 'start' and optional 'end' keys

**Example:**
```python
date_obj = extract_date_property(page)
if date_obj:
    print(f"Start: {date_obj['start']}")
```

---

#### `extract_days_and_time(page) -> Tuple[List[str], Optional[str]]`

Extracts day of week and time slot from a Notion page.

**Parameters:**
- `page` (Dict): Notion page object

**Returns:**
- `Tuple`: (list of day names, time slot string or None)

**Example:**
```python
days, time = extract_days_and_time(page)
print(f"Days: {days}, Time: {time}")
# Output: Days: ['1-Monday', '3-Wednesday'], Time: '0600'
```

---

#### `parse_time_slot(time_slot) -> Tuple[int, int]`

Parses a time slot string in HHMM format.

**Parameters:**
- `time_slot` (str): Time in HHMM format (e.g., "0600", "1330")

**Returns:**
- `Tuple[int, int]`: (hour, minute)

**Raises:**
- `ValueError`: If format is invalid

**Example:**
```python
hour, minute = parse_time_slot("1430")
print(f"Time: {hour}:{minute:02d}")  # Output: Time: 14:30
```

---

#### `get_page_event_id(page) -> Optional[str]`

Gets the Google Calendar event ID stored in a Notion page.

**Parameters:**
- `page` (Dict): Notion page object

**Returns:**
- `str` or `None`: Event ID if exists

**Example:**
```python
event_id = get_page_event_id(page)
if event_id:
    print(f"Already synced: {event_id}")
```

---

### Event Creation

#### `build_event_payload(title, date_obj) -> Dict`

Builds a Google Calendar event payload from a Notion date object.

**Parameters:**
- `title` (str): Event title
- `date_obj` (Dict): Notion date object with 'start' and optional 'end'

**Returns:**
- `Dict`: Google Calendar event payload

**Raises:**
- `ValueError`: If date object is invalid

**Example:**
```python
date_obj = {'start': '2025-10-25T14:00:00'}
payload = build_event_payload("Doctor Appointment", date_obj)
# Returns: {"summary": "Doctor Appointment", "start": {...}, "end": {...}}
```

---

#### `build_event_payload_from_time(title, event_datetime, duration_hours=1) -> Dict`

Builds an event payload from a datetime and duration.

**Parameters:**
- `title` (str): Event title
- `event_datetime` (datetime): Event start time
- `duration_hours` (int, optional): Event duration (default: 1)

**Returns:**
- `Dict`: Google Calendar event payload

**Example:**
```python
from datetime import datetime
dt = datetime(2025, 10, 25, 9, 0)
payload = build_event_payload_from_time("Meeting", dt, duration_hours=2)
```

---

#### `create_calendar_event(service, calendar_id, event_payload) -> Dict`

Creates a new event in Google Calendar.

**Parameters:**
- `service`: Google Calendar service object
- `calendar_id` (str): Calendar ID (e.g., 'primary')
- `event_payload` (Dict): Event data

**Returns:**
- `Dict`: Created event with ID

**Note:** Returns dummy event in dry-run mode.

**Example:**
```python
service = build_calendar_service()
payload = {...}
event = create_calendar_event(service, 'primary', payload)
print(f"Created: {event['id']}")
```

---

#### `update_calendar_event(service, calendar_id, event_id, event_payload) -> Dict`

Updates an existing event in Google Calendar.

**Parameters:**
- `service`: Google Calendar service object
- `calendar_id` (str): Calendar ID
- `event_id` (str): Existing event ID
- `event_payload` (Dict): Updated event data

**Returns:**
- `Dict`: Updated event

**Example:**
```python
updated = update_calendar_event(service, 'primary', 'event123', payload)
```

---

### Notion Updates

#### `notion_patch_event_id(notion, page_id, event_id) -> None`

Writes the Google Calendar event ID back to a Notion page.

**Parameters:**
- `notion` (NotionClient): Notion client
- `page_id` (str): Notion page ID
- `event_id` (str): Google Calendar event ID

**Example:**
```python
notion_patch_event_id(notion, "page123", "event456")
```

---

### Sync Functions

#### `sync_page_with_date(notion, service, calendar_id, page, title, date_obj) -> None`

Syncs a Notion page that has a specific date to Google Calendar.

**Parameters:**
- `notion` (NotionClient): Notion client
- `service`: Google Calendar service
- `calendar_id` (str): Calendar ID
- `page` (Dict): Notion page object
- `title` (str): Event title
- `date_obj` (Dict): Date object from Notion

**Example:**
```python
sync_page_with_date(notion, service, 'primary', page, "Meeting", date_obj)
```

---

#### `sync_page_with_recurring(notion, service, calendar_id, page, title, days, time_slot) -> None`

Syncs a Notion page with recurring day/time schedule.

**Parameters:**
- `notion` (NotionClient): Notion client
- `service`: Google Calendar service
- `calendar_id` (str): Calendar ID
- `page` (Dict): Notion page object
- `title` (str): Event title
- `days` (List[str]): List of day names
- `time_slot` (str): Time in HHMM format

**Example:**
```python
days = ['Monday', 'Wednesday', 'Friday']
sync_page_with_recurring(notion, service, 'primary', page, "Workout", days, "0600")
```

---

#### `sync_page(notion, service, calendar_id, page) -> None`

Main sync function for a single Notion page.

**Parameters:**
- `notion` (NotionClient): Notion client
- `service`: Google Calendar service
- `calendar_id` (str): Calendar ID
- `page` (Dict): Notion page object

**Example:**
```python
for page in pages:
    sync_page(notion, service, 'primary', page)
```

---

#### `run_sync(dry_run=True, max_pages=None) -> None`

Runs the complete sync process.

**Parameters:**
- `dry_run` (bool, optional): If True, no changes are made (default: True)
- `max_pages` (int, optional): Limit number of pages to process

**Example:**
```python
# Dry run
run_sync(dry_run=True)

# Actual sync
run_sync(dry_run=False)

# Test with 5 pages
run_sync(dry_run=True, max_pages=5)
```

---

## Constants

### Notion Property Names

```python
NOTION_TITLE_PROP = "Name"              # Title property
NOTION_DATE_PROP = "Date"               # Date property
NOTION_EVENT_ID_PROP = "Google Event ID"  # Text property for event ID
NOTION_DAY_PROP = "Day of the Week"    # Multi-select property
NOTION_TIME_PROP = "Time Slot"         # Text property for time
```

### Day Mapping

```python
DAY_MAP = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}
```

---

## Usage Examples

### Example 1: Custom Sync Script

```python
import os
from dotenv import load_dotenv
from notion_calendar_sync import (
    validate_environment,
    build_notion_client,
    build_calendar_service,
    query_notion_database,
    sync_page
)

# Load environment
load_dotenv()

# Validate setup
validate_environment()

# Build clients
notion = build_notion_client()
service = build_calendar_service()

# Query database
database_id = os.getenv("NOTION_DATABASE_ID")
pages = query_notion_database(notion, database_id)

# Sync only pages with specific tag
for page in pages:
    props = page.get("properties", {})
    tags = props.get("Tags", {}).get("multi_select", [])
    
    if any(tag["name"] == "Important" for tag in tags):
        sync_page(notion, service, 'primary', page)
```

### Example 2: Custom Event Creation

```python
from datetime import datetime, timedelta
from notion_calendar_sync import (
    build_calendar_service,
    build_event_payload_from_time,
    create_calendar_event
)

service = build_calendar_service()

# Create event for tomorrow at 2 PM
tomorrow = datetime.now() + timedelta(days=1)
tomorrow = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)

payload = build_event_payload_from_time(
    "Custom Event",
    tomorrow,
    duration_hours=2
)

event = create_calendar_event(service, 'primary', payload)
print(f"Created event: {event['id']}")
```

### Example 3: Batch Processing with Filters

```python
from notion_calendar_sync import (
    build_notion_client,
    build_calendar_service,
    sync_page
)

notion = build_notion_client()
service = build_calendar_service()

# Query with filter
response = notion.databases.query(
    database_id="your_db_id",
    filter={
        "property": "Status",
        "select": {
            "equals": "Ready to Sync"
        }
    }
)

# Sync filtered pages
for page in response["results"]:
    sync_page(notion, service, 'primary', page)
```

---

## Error Handling

All functions may raise the following exceptions:

- `ValueError`: Invalid input or configuration
- `FileNotFoundError`: Required files not found
- `HttpError`: Google API errors
- `Exception`: Notion API errors or general errors

**Example Error Handling:**

```python
from googleapiclient.errors import HttpError

try:
    run_sync(dry_run=False)
except ValueError as e:
    print(f"Configuration error: {e}")
except HttpError as e:
    print(f"Google API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Customization

### Change Property Names

If your Notion database uses different property names:

```python
# At the top of the script
NOTION_TITLE_PROP = "Task"              # Instead of "Name"
NOTION_DATE_PROP = "Due Date"           # Instead of "Date"
NOTION_DAY_PROP = "Weekdays"            # Instead of "Day of the Week"
```

### Change Event Duration

For recurring events, modify:

```python
def sync_page_with_recurring(...):
    # Change duration_hours parameter
    payload = build_event_payload_from_time(title, event_datetime, duration_hours=2)
```

### Add Custom Fields

Extend event payloads with additional data:

```python
def build_custom_event_payload(title, date_obj, description=None, location=None):
    payload = build_event_payload(title, date_obj)
    
    if description:
        payload["description"] = description
    if location:
        payload["location"] = location
    
    return payload
```

---

## Best Practices

1. **Always validate environment first:**
   ```python
   validate_environment()
   ```

2. **Use dry-run for testing:**
   ```python
   run_sync(dry_run=True, max_pages=5)
   ```

3. **Handle errors gracefully:**
   ```python
   try:
       sync_page(notion, service, calendar_id, page)
   except Exception as e:
       logger.error(f"Failed to sync page: {e}")
       continue  # Keep processing other pages
   ```

4. **Add rate limiting for large databases:**
   ```python
   import time
   for page in pages:
       sync_page(notion, service, calendar_id, page)
       time.sleep(0.5)  # Increase delay
   ```

---

## See Also

- [Setup Guide](SETUP_GUIDE.md) - Initial setup instructions
- [Examples](EXAMPLES.md) - Real-world usage examples
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Notion API Documentation](https://developers.notion.com/)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
