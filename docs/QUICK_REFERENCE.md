

# Quick Reference Guide - New Features

## 🎯 Overview of Updates

This guide covers the new features added to the Notion_Database_to_Calendar sync tool:

1. **Tasks Property** - Updated title field name
2. **Duration Support** - Custom event lengths
3. **Frequency Logic** - More flexible recurring patterns
4. **Priority Colors** - Visual organization in calendar

---

## 📝 Updated Property Mapping

### Before (v1.0)
```
Property Name: "Name"
Duration: Always 1 hour
Frequency: Always weekly
Priority: Not supported
```

### After (v2.0)
```
Property Name: "Tasks"
Duration: From Notion field (minutes → hours)
Frequency: Daily/Weekly/Bi-Weekly/Monthly/Bi-Monthly
Priority: High (Red) / Medium (Yellow) / Low (Green)
```

---

## ⏱️ Duration Field

### How It Works
- **Notion Field Type**: Number
- **Unit**: Minutes
- **Conversion**: Automatically converted to hours for Google Calendar
- **Default**: 60 minutes (1 hour) if not specified

### Examples
```
Duration: 30  → 30-minute event
Duration: 60  → 1-hour event (default)
Duration: 90  → 1.5-hour event
Duration: 120 → 2-hour event
```

### Use Cases
```
Morning Meditation → 15 minutes
Team Standup      → 30 minutes
Workout Session   → 60 minutes
Sprint Planning   → 90 minutes
Deep Work Block   → 120 minutes
```

---

## 🔄 Frequency Logic

### Supported Frequencies

#### **Daily**
- **Pattern**: Every single day
- **Ignores**: Day of the Week field
- **Example**: Morning routine, daily standup
- **Warning**: Creates many events!

```
Tasks: "Morning Coffee"
Frequency: Daily
Time Slot: 0700
Duration: 15
→ Creates event at 7:00 AM every day until end of year
```

#### **Weekly** (Default)
- **Pattern**: Same day(s) every week
- **Uses**: Day of the Week field
- **Example**: Monday team meeting

```
Tasks: "Team Meeting"
Frequency: Weekly
Day of the Week: 1-Monday
Time Slot: 0930
Duration: 60
→ Creates event every Monday at 9:30 AM
```

#### **Bi-Weekly**
- **Pattern**: Every 14 days
- **Uses**: Day of the Week field
- **Example**: Sprint planning every other Monday

```
Tasks: "Sprint Planning"
Frequency: Bi-Weekly
Day of the Week: 1-Monday
Time Slot: 1000
Duration: 90
→ Creates event every other Monday at 10:00 AM
```

#### **Monthly**
- **Pattern**: Same date every month (using relativedelta)
- **Uses**: Day of the Week field for initial occurrence
- **Example**: Monthly review

```
Tasks: "Monthly Budget Review"
Frequency: Monthly
Day of the Week: 1-Monday
Time Slot: 1400
Duration: 120
→ Creates event on same day each month
```

#### **Bi-Monthly**
- **Pattern**: Every 2 months
- **Uses**: Day of the Week field for initial occurrence
- **Example**: Quarterly planning

```
Tasks: "Quarterly Goals Review"
Frequency: Bi-Monthly
Day of the Week: 3-Wednesday
Time Slot: 1500
Duration: 90
→ Creates event every 2 months
```

### Frequency Comparison Table

| Frequency | Days Between | Example Use Case |
|-----------|--------------|------------------|
| Daily | 1 | Morning routine, medication |
| Weekly | 7 | Team meetings, classes |
| Bi-Weekly | 14 | Sprint planning, payday |
| Monthly | ~30 | Bill payments, reviews |
| Bi-Monthly | ~60 | Quarterly checks, dentist |

---

## 🎨 Priority-Based Colors

### Color Mapping

| Priority | Color | Google Calendar ID | Use Case |
|----------|-------|-------------------|----------|
| **High** | 🔴 Red | 11 | Critical tasks, deadlines |
| **Medium** | 🟡 Yellow | 5 | Important but not urgent |
| **Low** | 🟢 Green | 10 | Nice to have, flexible |

### Visual Calendar

```
Calendar View:
┌─────────────────────────────────────┐
│ Monday, December 10                 │
├─────────────────────────────────────┤
│ 🔴 0630 - Workout (High)            │
│ 🟡 0930 - Team Meeting (Medium)     │
│ 🟢 1200 - Lunch Walk (Low)          │
│ 🔴 1400 - Client Presentation (High)│
└─────────────────────────────────────┘
```

### How to Set Priority

In Notion:
1. Add "Priority" Select property
2. Create options: High, Medium, Low
3. Assign to each task

The script will automatically apply colors to calendar events.

---

## 🔧 Configuration Examples

### Example 1: Morning Routine (Daily, 30 min, High Priority)
```
Tasks: Wake up / Wash Face / Brush Teeth
Day of the Week: (leave empty for Daily)
Time Slot: 0600
Duration: 30
Frequency: Daily
Priority: High

Result: Red 30-minute event every day at 6:00 AM
```

### Example 2: Gym Workout (Weekly, 1 hour, Medium Priority)
```
Tasks: Gym Workout
Day of the Week: 1-Monday, 3-Wednesday, 5-Friday
Time Slot: 0630
Duration: 60
Frequency: Weekly
Priority: Medium

Result: Yellow 1-hour events on M/W/F at 6:30 AM
```

### Example 3: Budget Review (Monthly, 2 hours, High Priority)
```
Tasks: Monthly Budget Review
Day of the Week: 7-Sunday
Time Slot: 1400
Duration: 120
Frequency: Monthly
Priority: High

Result: Red 2-hour event on same Sunday each month at 2:00 PM
```

### Example 4: Meditation (Daily, 15 min, Low Priority)
```
Tasks: Meditate / Stretch / Pray
Day of the Week: (ignored)
Time Slot: 0545
Duration: 15
Frequency: Daily
Priority: Low

Result: Green 15-minute event every day at 5:45 AM
```

---

## 🚀 Testing Your Setup

### Step 1: Dry Run with One Page
```bash
python notion_calendar_sync.py --max-pages 1
```

**Look for in logs:**
```
Duration: 30 minutes = 0.5 hours
Created 1 recurring events (Daily) for page abc123
```

### Step 2: Verify Property Extraction
Check logs show:
- ✅ Tasks field is read correctly
- ✅ Duration is converted to hours
- ✅ Priority is detected
- ✅ Frequency is applied

### Step 3: Test Live with Limited Pages
```bash
python notion_calendar_sync.py --no-dry-run --max-pages 3
```

### Step 4: Verify in Google Calendar
- [ ] Events appear at correct times
- [ ] Duration matches expected length
- [ ] Colors match priority levels
- [ ] Frequency pattern is correct

---

## ⚠️ Common Issues & Solutions

### Issue 1: "No valid title" Warning
```
Problem: NOTION_TITLE_PROP doesn't match your database
Solution: Verify property is named "Tasks" in Notion
```

### Issue 2: Duration Not Applied
```
Problem: Duration field is empty or wrong type
Solution: 
- Ensure "Duration" is Number type in Notion
- Enter duration in minutes (e.g., 30, 60, 90)
- Check logs: "Duration: X minutes = Y hours"
```

### Issue 3: Frequency Not Working
```
Problem: Events still created weekly
Solution:
- Ensure "Frequency" is Select type
- Options must match exactly: Daily, Weekly, Bi-Weekly, Monthly, Bi-Monthly
- Check logs: "Created X recurring events (Frequency) for page..."
```

### Issue 4: Colors Not Showing
```
Problem: All events same color in calendar
Solution:
- Ensure "Priority" is Select type
- Options must be: High, Medium, Low (case-sensitive)
- Google Calendar may take a few minutes to show colors
```

### Issue 5: Too Many Events Created
```
Problem: Daily frequency created hundreds of events
Solution:
- Daily creates one event per day until end of year
- Use Weekly for most recurring tasks
- Consider limiting with --max-pages first
```

---

## 📊 Recommended Workflow

### 1. Set Up New Task in Notion
```
1. Add task title in "Tasks" field
2. Choose schedule:
   - Specific date? Fill "Date" field
   - Recurring? Fill "Day of the Week" + "Time Slot"
3. Set "Duration" (minutes)
4. Set "Priority" (High/Medium/Low)
5. Set "Frequency" (Daily/Weekly/etc.)
```

### 2. Test Sync
```bash
# Dry run to preview
python notion_calendar_sync.py --max-pages 5

# Check logs carefully
# Look for warnings or errors
```

### 3. Live Sync
```bash
# Sync all tasks
python notion_calendar_sync.py --no-dry-run
```

### 4. Verify Calendar
- Open Google Calendar
- Check that events:
  - Appear at correct times
  - Have correct duration
  - Show correct colors
  - Follow frequency pattern

---

## 💡 Pro Tips

### Tip 1: Use Descriptive Task Names
```
❌ Bad: "Meeting"
✅ Good: "Team Standup - Engineering"
```

### Tip 2: Consistent Duration Patterns
```
Quick tasks: 15-30 minutes
Standard meetings: 60 minutes
Deep work: 90-120 minutes
```

### Tip 3: Strategic Color Usage
```
🔴 Red (High): Deadlines, critical meetings, must-do tasks
🟡 Yellow (Medium): Important but flexible, team activities
🟢 Green (Low): Self-care, optional, aspirational
```

### Tip 4: Frequency Selection
```
Daily: Only for true daily habits (meditation, medication)
Weekly: Most recurring tasks (meetings, workouts)
Bi-Weekly: Paydays, alternating responsibilities
Monthly: Bills, reviews, maintenance
```

### Tip 5: Batch Testing
```bash
# Test new tasks first
python notion_calendar_sync.py --max-pages 3

# Then sync all
python notion_calendar_sync.py --no-dry-run
```

---

## 📞 Need Help?

### Check Logs First
```bash
# Look for these indicators:
[INFO] Duration: X minutes = Y hours     ← Duration working
[INFO] Created X recurring events (Type) ← Frequency working
[WARNING] Invalid time format             ← Fix time slot
[ERROR] Failed to write event ID          ← Notion permission issue
```

### Common Log Messages
```
✅ "Environment validation passed" - Setup correct
✅ "Wrote event ID to Notion page" - Sync successful
⚠️ "Skipping page: no valid title" - Check Tasks field
⚠️ "Invalid time format" - Fix Time Slot to HHMM
❌ "Missing required environment variables" - Check .env file
```

---

## 🎓 Learning Examples

### Beginner: Simple Morning Routine
```
Tasks: Morning Coffee
Time Slot: 0700
Duration: 15
Frequency: Daily
Priority: Low
```

### Intermediate: Work Schedule
```
Tasks: Team Standup
Day of the Week: 1-Monday, 2-Tuesday, 3-Wednesday, 4-Thursday, 5-Friday
Time Slot: 0930
Duration: 30
Frequency: Weekly
Priority: Medium
```

### Advanced: Complex Recurring Pattern
```
Tasks: Sprint Planning
Day of the Week: 1-Monday
Time Slot: 1000
Duration: 90
Frequency: Bi-Weekly
Priority: High
```

---

## 🔄 Quick Command Reference

```bash
# Dry run - preview changes
python notion_calendar_sync.py

# Dry run - test few pages
python notion_calendar_sync.py --max-pages 3

# Live sync - test one page
python notion_calendar_sync.py --no-dry-run --max-pages 1

# Live sync - all pages
python notion_calendar_sync.py --no-dry-run

# Help
python notion_calendar_sync.py --help
```

---

**Updated**: December 10, 2025  
**Version**: 2.0.0  
**Author**: Marlin Z
