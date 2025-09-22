pip install -r Requirements.txt

# Notion Database to Calendar

This project automates the transformation of Notion database items into Google Calendar events for streamlined planning and scheduling.

## Purpose

Create a connector that syncs tasks from a Notion database to Google Calendar, enabling easy management of routines and events.

## Features

- **Fetch Tasks from Notion:** Connects to a Notion database and retrieves all tasks, supporting pagination.
- **Google Calendar Integration:** Uses a Google service account to create calendar events for each task.
- **Day and Time Mapping:** Maps Notion "Day of the Week" and "Time Slot" properties to calendar event dates and times.
- **Recurring Events:** If a Notion page does not have a "Date" property, events are created for each specified weekday and time slot from today until the end of the year.
- **Deduplication:** Checks if a task is already linked to a Google Calendar event to avoid duplicates.
- **Error Handling:** Skips tasks with missing or invalid properties and logs warnings.

## How It Works

1. **Configuration:**  
	- Set up environment variables for Notion and Google API credentials.
	- Required files:  
	  - `GOOGLE_SERVICE_ACCOUNT.json` (Google API credentials)
	  - `.env` file with Notion and Google Calendar IDs

2. **Transformation Logic:**  
	- The script (`Transformation.py`) fetches all tasks from the Notion database.
	- For each task, it reads the "Tasks", "Day of the Week", and "Time Slot" properties.
	- If a "Date" property is present, it creates a single event. If not, it creates events for each matching weekday until the end of the year.
	- Creates a Google Calendar event and updates the Notion page with the event ID.

3. **Error Handling:**  
	- If a task is missing required properties (e.g., "Tasks"), it is skipped and a warning is logged.
	- Invalid time formats are also skipped.

## Requirements

- Python 3.8+
- Notion API token
- Google service account credentials
- Required Python packages (see `Requirements.txt`):
  - `notion-client`
  - `google-api-python-client`
  - `google-auth`
  - `python-dotenv`

## Usage

1. Install dependencies:
	```bash
	pip install -r Requirements.txt
	```
2. Set up your `.env` file with the following variables:
	```
	NOTION_API_KEY=your_notion_token
	NOTION_DATABASE_ID=your_database_id
	GOOGLE_APPLICATION_CREDENTIALS=GOOGLE_SERVICE_ACCOUNT.json
	GOOGLE_CALENDAR_ID=your_calendar_id (optional, defaults to 'primary')
	TIMEZONE=America/New_York
	```
3. Run the transformation script:
	```bash
	python Transformation.py
	```

## Notion Database Structure

- **Tasks:** Title of the task (required)
- **Day of the Week:** Multi-select (e.g., "1-Monday", "2-Tuesday", ...)
- **Time Slot:** Text (e.g., "0600" for 6:00 AM)
- **Date:** (Optional, for single events)
- **Frequency:** (Optional, e.g., "Daily")

## Troubleshooting

- If you see warnings about missing properties, ensure all Notion database rows have the required fields.
- Check your credentials and environment variables if API requests fail.