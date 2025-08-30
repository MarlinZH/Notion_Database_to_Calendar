from notion_client import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv

notion = Client(auth="your_notion_secret")
database_id = "your_database_id"

days_of_week = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

def get_next_weekday(base_date, target_weekday):
    days_ahead = target_weekday - base_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return base_date + timedelta(days=days_ahead)

def spread_tasks():
    today = datetime.now()
    tasks = notion.databases.query(database_id=database_id)["results"]

    for task in tasks:
        props = task["properties"]
        task_name = props["Name"]["title"][0]["text"]["content"]
        time_slot = props["Time Slot"]["rich_text"][0]["text"]["content"]
        days = [d["name"] for d in props["Days"]["multi_select"]]

        for day in days:
            weekday_index = days_of_week[day]
            target_date = get_next_weekday(today, weekday_index)
            hour, minute = map(int, time_slot.split(":"))
            task_datetime = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Create calendar entry in another Notion DB
            notion.pages.create(
                parent={"database_id": "your_calendar_db_id"},
                properties={
                    "Name": {"title": [{"text": {"content": task_name}}]},
                    "Date": {"date": {"start": task_datetime.isoformat()}},
                    # optionally link to original task
                }
            )

spread_tasks()
