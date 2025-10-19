# Troubleshooting Guide

This guide helps you resolve common issues with the Notion Database to Calendar sync tool.

## Table of Contents

1. [Environment Setup Issues](#environment-setup-issues)
2. [Notion API Issues](#notion-api-issues)
3. [Google Calendar Issues](#google-calendar-issues)
4. [Sync Issues](#sync-issues)
5. [Performance Issues](#performance-issues)
6. [Common Error Messages](#common-error-messages)

---

## Environment Setup Issues

### Issue: "Missing required environment variables"

**Error Message:**
```
ValueError: Missing required environment variables: NOTION_API_KEY, NOTION_DATABASE_ID
```

**Causes:**
- `.env` file doesn't exist
- Variables not set correctly in `.env`
- Typo in variable names

**Solutions:**

1. Check if `.env` file exists:
   ```bash
   ls -la .env
   ```

2. Create from example:
   ```bash
   cp .env.example .env
   ```

3. Verify format (no spaces around `=`):
   ```env
   # ✅ Correct
   NOTION_API_KEY=secret_abc123
   
   # ❌ Wrong
   NOTION_API_KEY = secret_abc123
   ```

4. Check variable names match exactly:
   - `NOTION_API_KEY` (not `NOTION_TOKEN`)
   - `NOTION_DATABASE_ID` (not `DATABASE_ID`)

### Issue: "Google service account file not found"

**Error Message:**
```
FileNotFoundError: Google service account file not found: GOOGLE_SERVICE_ACCOUNT.json
```

**Solutions:**

1. Check file exists:
   ```bash
   ls -la GOOGLE_SERVICE_ACCOUNT.json
   ```

2. Verify filename matches exactly (case-sensitive)

3. Ensure file is in project root directory

4. Check `.env` points to correct path:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=GOOGLE_SERVICE_ACCOUNT.json
   ```

### Issue: Python Module Not Found

**Error Message:**
```
ModuleNotFoundError: No module named 'notion_client'
```

**Solutions:**

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. If using virtual environment, activate it first:
   ```bash
   # macOS/Linux
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

3. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```

---

## Notion API Issues

### Issue: "Notion API authentication failed"

**Symptoms:**
- Cannot connect to Notion
- "unauthorized" error
- "invalid_token" error

**Solutions:**

1. **Verify token is correct:**
   - Token should start with `secret_`
   - No extra spaces or line breaks
   - Copy-paste carefully from Notion integrations page

2. **Check integration is connected to database:**
   - Open your Notion database
   - Click "..." menu → "Add connections"
   - Verify your integration is listed
   - If not, add it

3. **Regenerate token if needed:**
   - Go to [Notion integrations](https://www.notion.so/my-integrations)
   - Click your integration
   - Generate new token
   - Update `.env` file

### Issue: "Database not found"

**Error Message:**
```
Notion API error: object_not_found
```

**Solutions:**

1. **Verify database ID:**
   ```
   https://www.notion.so/YOUR_DATABASE_ID?v=...
   ```
   Copy the 32-character ID (with hyphens)

2. **Check database is shared:**
   - Database must be shared with integration
   - Not just the page containing the database
   - Share the actual database view

3. **Test with notion-client directly:**
   ```python
   from notion_client import Client
   notion = Client(auth="your_token")
   db = notion.databases.retrieve(database_id="your_id")
   print(db["title"])
   ```

### Issue: Missing Properties

**Error Message:**
```
[WARNING] Skipping page abc123: no date property and missing Day of the Week or Time Slot
```

**Solutions:**

1. **Check property names match exactly:**
   - `Name` (Title)
   - `Date` (Date)
   - `Day of the Week` (Multi-select)
   - `Time Slot` (Text)
   - `Google Event ID` (Rich Text)

2. **Update property names in script if different:**
   ```python
   NOTION_TITLE_PROP = "Task"  # If you use "Task" instead of "Name"
   ```

3. **Ensure each page has required fields:**
   - Either `Date` is filled
   - OR both `Day of the Week` AND `Time Slot` are filled

---

## Google Calendar Issues

### Issue: "Calendar not accessible"

**Error Message:**
```
HttpError 403: Forbidden
```

**Solutions:**

1. **Share calendar with service account:**
   - Open Google Calendar settings
   - Find your calendar
   - "Share with specific people"
   - Add service account email
   - Grant "Make changes to events" permission

2. **Find service account email:**
   ```bash
   cat GOOGLE_SERVICE_ACCOUNT.json | grep "client_email"
   ```
   It looks like: `something@project-id.iam.gserviceaccount.com`

3. **Enable Google Calendar API:**
   - Go to Google Cloud Console
   - APIs & Services → Library
   - Search "Google Calendar API"
   - Click "Enable"

### Issue: Events Not Appearing

**Symptoms:**
- Script runs successfully
- No errors shown
- Events don't appear in calendar

**Solutions:**

1. **Verify you're using --no-dry-run:**
   ```bash
   python notion_calendar_sync.py --no-dry-run
   ```

2. **Check correct calendar:**
   - Verify `GOOGLE_CALENDAR_ID` in `.env`
   - Try using `primary` for main calendar

3. **Check calendar view:**
   - Ensure you're looking at correct date range
   - Recurring events start from today
   - Check "All calendars" are visible

4. **Test with API directly:**
   ```bash
   # List events
   python -c "from google.oauth2 import service_account; from googleapiclient.discovery import build; creds = service_account.Credentials.from_service_account_file('GOOGLE_SERVICE_ACCOUNT.json', scopes=['https://www.googleapis.com/auth/calendar']); service = build('calendar', 'v3', credentials=creds); events = service.events().list(calendarId='primary', maxResults=10).execute(); print(events)"
   ```

### Issue: Duplicate Events

**Symptoms:**
- Same event appears multiple times
- Events multiply on each sync

**Solutions:**

1. **Check "Google Event ID" property exists:**
   - Must be Rich Text type in Notion
   - Script writes event ID here to prevent duplicates

2. **Manual cleanup:**
   - Delete duplicate events in Google Calendar
   - Clear "Google Event ID" values in Notion
   - Run sync again

3. **Ensure property name matches:**
   ```python
   NOTION_EVENT_ID_PROP = "Google Event ID"  # Must match exactly
   ```

---

## Sync Issues

### Issue: Invalid Time Format

**Error Message:**
```
[WARNING] Invalid time format '6:00' for page xyz: Expected HHMM format (e.g., 0600), got: 6:00
```

**Solutions:**

1. **Use HHMM format:**
   - ✅ `0600` for 6:00 AM
   - ✅ `1330` for 1:30 PM
   - ✅ `2145` for 9:45 PM
   - ❌ `6:00`
   - ❌ `13:30`
   - ❌ `600`

2. **Batch update in Notion:**
   - Select all pages with wrong format
   - Edit Time Slot property
   - Use find/replace if needed

### Issue: Unknown Day Name

**Error Message:**
```
[WARNING] Unknown day 'Mon' for page abc123, skipping.
```

**Solutions:**

1. **Use full day names:**
   - ✅ `Monday`, `Tuesday`, etc.
   - ✅ `1-Monday`, `2-Tuesday`, etc. (with prefix)
   - ❌ `Mon`, `Tue`, etc.

2. **Update multi-select options:**
   - Go to database properties
   - Edit "Day of the Week" property
   - Rename options to full names

### Issue: Timezone Problems

**Symptoms:**
- Events appear at wrong time
- Off by several hours

**Solutions:**

1. **Check timezone setting:**
   ```env
   TIMEZONE=America/New_York  # Must be valid timezone
   ```

2. **Find your timezone:**
   - [List of timezones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
   - Use "TZ database name" column

3. **Match Notion workspace timezone:**
   - Go to Notion Settings
   - Check "Language & region"
   - Use same timezone in `.env`

---

## Performance Issues

### Issue: Sync Takes Too Long

**Symptoms:**
- Script runs for several minutes
- Lots of API calls

**Solutions:**

1. **Use filters in Notion:**
   - Create a view with only relevant pages
   - Use that view's database ID

2. **Increase rate limiting:**
   ```python
   time.sleep(0.5)  # Increase from 0.2 if getting rate limited
   ```

3. **Sync only recent changes:**
   - Add a "Last Synced" date property
   - Filter for pages modified since last sync

### Issue: Rate Limiting

**Error Message:**
```
HTTPError 429: Too Many Requests
```

**Solutions:**

1. **Increase delays between requests:**
   In the script, change:
   ```python
   time.sleep(0.2)  # to
   time.sleep(1.0)  # or higher
   ```

2. **Process fewer pages at once:**
   ```bash
   python notion_calendar_sync.py --max-pages 50
   ```

3. **Run less frequently:**
   - Instead of every hour, try every 6 hours
   - Reduce automated sync frequency

---

## Common Error Messages

### "SSL: CERTIFICATE_VERIFY_FAILED"

**Solutions:**
1. Update certificates:
   ```bash
   pip install --upgrade certifi
   ```

2. On macOS, run:
   ```bash
   /Applications/Python\ 3.x/Install\ Certificates.command
   ```

### "Connection reset by peer"

**Solutions:**
1. Check internet connection
2. Retry the sync
3. Add retry logic to script

### "Invalid grant"

**Solutions:**
1. Service account key may be expired
2. Download new key from Google Cloud Console
3. Update `GOOGLE_SERVICE_ACCOUNT.json`

### "Insufficient permissions"

**Solutions:**
1. Verify calendar sharing permissions
2. Ensure service account has "Make changes to events"
3. Check Google Calendar API is enabled

---

## Debugging Tips

### Enable Verbose Logging

Modify the script temporarily:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
```

### Test Individual Components

**Test Notion Connection:**
```python
from notion_client import Client
notion = Client(auth="your_token")
db = notion.databases.retrieve("your_db_id")
print("Connected to:", db["title"])
```

**Test Google Calendar Connection:**
```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file(
    'GOOGLE_SERVICE_ACCOUNT.json',
    scopes=['https://www.googleapis.com/auth/calendar']
)
service = build('calendar', 'v3', credentials=creds)
cals = service.calendarList().list().execute()
print("Accessible calendars:", [c['summary'] for c in cals['items']])
```

### Capture Full Logs

```bash
python notion_calendar_sync.py --no-dry-run 2>&1 | tee debug.log
```

---

## Getting Help

If you're still stuck:

1. **Check existing issues:**
   - [GitHub Issues](https://github.com/MarlinZH/Notion_Database_to_Calendar/issues)
   - Search for similar problems

2. **Create a new issue with:**
   - Detailed description of the problem
   - Error messages (remove sensitive data!)
   - Steps to reproduce
   - Your environment:
     - Python version: `python --version`
     - OS: Windows/macOS/Linux
     - Package versions: `pip list`

3. **Include relevant logs:**
   ```bash
   python notion_calendar_sync.py > debug.log 2>&1
   ```
   Then share debug.log (after removing tokens/IDs)

---

## Prevention Tips

### Regular Maintenance

1. **Keep dependencies updated:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Test after updates:**
   ```bash
   python notion_calendar_sync.py --max-pages 2
   ```

3. **Monitor logs regularly:**
   - Check for warnings
   - Address issues early

### Best Practices

1. **Always use dry-run first**
2. **Test with --max-pages before full sync**
3. **Keep backups of your .env file**
4. **Document any custom modifications**
5. **Use version control for custom changes**

---

Still having issues? Open a [GitHub Issue](https://github.com/MarlinZH/Notion_Database_to_Calendar/issues) and we'll help you out!
