# CHANGELOG

## [2.0.0] - 2025-12-10

### 🎉 Major Updates - Custom Database Alignment

This release updates the codebase to align with Marlin's custom Notion Routine Database structure and adds significant new functionality.

### Added

#### **Duration Support**
- Added `extract_duration()` function to read Duration field from Notion (in minutes)
- Duration is automatically converted to hours for Google Calendar events
- Default duration is 1 hour if not specified
- Updated `build_event_payload_from_time()` to accept `duration_hours` parameter
- Duration now properly affects event end times in calendar

#### **Frequency-Based Recurring Events**
- Implemented intelligent frequency logic for recurring events
- Supported frequencies:
  - **Daily**: Creates events every day
  - **Weekly**: Creates events every 7 days (default)
  - **Bi-Weekly**: Creates events every 14 days
  - **Monthly**: Creates events every month (uses relativedelta)
  - **Bi-Monthly**: Creates events every 2 months (uses relativedelta)
- Added `get_next_occurrence()` function to calculate next event date
- Frequency defaults to "Weekly" if not specified
- Daily frequency ignores "Day of the Week" and creates events every single day

#### **Priority-Based Color Coding**
- Added priority extraction with `extract_priority()` function
- Integrated Google Calendar color IDs:
  - **High Priority**: Red (color ID 11)
  - **Medium Priority**: Yellow/Banana (color ID 5)
  - **Low Priority**: Green/Basil (color ID 10)
- Colors are automatically applied to calendar events based on Notion Priority field
- Added `get_event_color()` helper function

#### **Enhanced Logging**
- Added debug logging for duration extraction
- Improved logging to show frequency type in sync results
- Better error messages for invalid time formats

### Changed

#### **Property Name Updates**
- **BREAKING**: Changed `NOTION_TITLE_PROP` from "Name" to "Tasks"
  - This aligns with Marlin's Notion database structure
  - Update your Notion database to use "Tasks" as the title field, or rename back to "Name"

#### **Enhanced Function Signatures**
- `sync_page_with_date()` now accepts `priority` parameter
- `sync_page_with_recurring()` now accepts:
  - `duration_hours` parameter (default: 1.0)
  - `priority` parameter (default: None)
  - `frequency` parameter (default: "Weekly")
- `build_event_payload()` now accepts `color_id` parameter
- `build_event_payload_from_time()` now accepts:
  - `duration_hours` as float instead of int
  - `color_id` parameter

#### **Dependencies**
- Added `python-dotenv` to requirements (already was used, now explicit)
- Imported `relativedelta` from `dateutil.relativedelta` for monthly recurrence

### Technical Details

#### **New Constants**
```python
NOTION_TITLE_PROP = "Tasks"  # Changed from "Name"
NOTION_DURATION_PROP = "Duration"
NOTION_PRIORITY_PROP = "Priority"
NOTION_FREQUENCY_PROP = "Frequency"

FREQUENCY_MAP = {
    "Daily": 1,
    "Weekly": 7,
    "Bi-Weekly": 14,
    "Monthly": None,  # Uses relativedelta
    "Bi-Monthly": None,  # Uses relativedelta
}

PRIORITY_COLORS = {
    "High": "11",      # Red
    "Medium": "5",     # Yellow/Banana
    "Low": "10",       # Green/Basil
}
```

#### **New Functions**
- `extract_duration(page)` → float: Returns duration in hours
- `extract_priority(page)` → Optional[str]: Returns priority level
- `extract_frequency(page)` → Optional[str]: Returns frequency setting
- `get_event_color(priority)` → Optional[str]: Maps priority to color ID
- `get_next_occurrence(current, frequency, weekday_num)` → datetime: Calculates next event

### Database Schema Requirements

Your Notion database should now have these properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| **Tasks** | Title | Yes | Event title (changed from "Name") |
| **Date** | Date | Conditional* | Specific date for one-time events |
| **Day of the Week** | Multi-select | Conditional* | Days for recurring events (1-Monday, 2-Tuesday, etc.) |
| **Time Slot** | Text | Conditional* | Time in HHMM format (e.g., "0630") |
| **Duration** | Number | No | Duration in minutes (defaults to 60) |
| **Priority** | Select | No | High/Medium/Low for color coding |
| **Frequency** | Select | No | Daily/Weekly/Bi-Weekly/Monthly/Bi-Monthly (defaults to Weekly) |
| **Google Event ID** | Rich Text | No | Auto-populated by script |

*Either "Date" OR both "Day of the Week" and "Time Slot" are required.

### Examples

#### Example 1: Daily Morning Routine with Duration
```
Tasks: "Morning Meditation"
Day of the Week: (ignored for Daily)
Time Slot: "0600"
Duration: 30 (minutes)
Frequency: Daily
Priority: High
→ Creates 30-minute events at 6:00 AM every day (red color)
```

#### Example 2: Bi-Weekly Team Meeting
```
Tasks: "Sprint Planning"
Day of the Week: 1-Monday
Time Slot: "1000"
Duration: 90 (minutes)
Frequency: Bi-Weekly
Priority: Medium
→ Creates 90-minute events every other Monday at 10:00 AM (yellow color)
```

#### Example 3: Monthly Review
```
Tasks: "Monthly Budget Review"
Day of the Week: 1-Monday (first Monday of each month will be auto-selected)
Time Slot: "1400"
Duration: 120 (minutes)
Frequency: Monthly
Priority: High
→ Creates 2-hour events on the same day of month, every month (red color)
```

### Migration Guide

#### From Version 1.x to 2.0

1. **Update Property Names in Notion**:
   - Rename "Name" property to "Tasks" (or update `NOTION_TITLE_PROP` in code)
   - Ensure "Google Event ID" is Rich Text type (not Number)

2. **Add New Properties** (all optional):
   - Add "Duration" (Number) for custom event lengths
   - Add "Priority" (Select) with options: High, Medium, Low
   - Add "Frequency" (Select) with options: Daily, Weekly, Bi-Weekly, Monthly, Bi-Monthly

3. **Update Dependencies**:
   ```bash
   pip install --upgrade -r Requirements.txt
   ```

4. **Test with Dry Run**:
   ```bash
   python notion_calendar_sync.py --max-pages 3
   ```

5. **Review Logs**: Check that duration, priority, and frequency are being read correctly

6. **Run Live Sync**:
   ```bash
   python notion_calendar_sync.py --no-dry-run --max-pages 1
   ```

### Backward Compatibility

- ✅ Works without Duration field (defaults to 1 hour)
- ✅ Works without Priority field (no color applied)
- ✅ Works without Frequency field (defaults to Weekly)
- ✅ Existing functionality for Date-based events unchanged
- ⚠️ **Breaking**: Must update NOTION_TITLE_PROP or rename property to "Tasks"

### Known Issues

- Monthly and Bi-Monthly frequencies calculate based on relativedelta, not actual calendar months
- Daily frequency creates many events; recommend using with caution
- Color coding requires Google Calendar API permissions (already included in scopes)

### Testing Checklist

- [x] Duration field extraction and conversion
- [x] Priority-based color coding
- [x] Daily frequency (creates events every day)
- [x] Weekly frequency (original behavior)
- [x] Bi-Weekly frequency
- [x] Monthly frequency (relativedelta)
- [x] Bi-Monthly frequency (relativedelta)
- [x] Backward compatibility (missing optional fields)
- [x] Dry-run mode with new features
- [x] Event ID writing to Notion

### Contributors

- Marlin Z (@MarlinZH) - Original implementation and custom requirements
- Claude (Anthropic) - Feature implementation and documentation

---

## [1.0.0] - 2024-10-24

### Initial Release

- Basic Notion to Google Calendar sync
- Support for Date property (one-time events)
- Support for Day of the Week + Time Slot (recurring weekly events)
- Dry-run mode for safe testing
- Environment validation
- Comprehensive error handling
- Documentation and examples
