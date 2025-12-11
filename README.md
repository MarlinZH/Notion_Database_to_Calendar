# Notion Database to Calendar

[![Run Tests](https://github.com/MarlinZH/Notion_Database_to_Calendar/workflows/Run%20Tests/badge.svg)](https://github.com/MarlinZH/Notion_Database_to_Calendar/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)

A powerful automation tool that syncs your Notion database tasks to Google Calendar with advanced features for custom durations, flexible recurring patterns, and priority-based color coding.

## ✨ Features

- **🔄 One-Way Sync:** Notion → Google Calendar
- **📅 Flexible Scheduling:**
  - Single events with specific dates
  - Recurring events based on day of week and time
  - **NEW:** Multiple frequency options (Daily, Weekly, Bi-Weekly, Monthly, Bi-Monthly)
- **⏱️ Custom Duration:** Set event lengths in minutes (auto-converts to hours)
- **🎨 Priority Colors:** Visual organization with High (Red), Medium (Yellow), Low (Green)
- **🛡️ Safe Testing:** Dry-run mode to preview changes
- **🔍 Smart Deduplication:** Prevents duplicate events
- **⚡ Batch Processing:** Handles large databases with pagination
- **🔧 Error Handling:** Comprehensive validation and error reporting
- **📊 Progress Tracking:** Detailed logging and sync statistics

## 🆕 What's New in v2.0

- ✅ **Duration Support** - Custom event lengths from Notion (15 min to 2+ hours)
- ✅ **Frequency Options** - Daily, Weekly, Bi-Weekly, Monthly, Bi-Monthly recurring patterns
- ✅ **Priority Colors** - Automatic color coding based on task priority
- ✅ **Tasks Property** - Updated to match custom database structure
- ✅ **Enhanced Logging** - Better visibility into sync process

See [CHANGELOG.md](CHANGELOG.md) for full details.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Notion account with a database
- Google account with Calendar access

### Installation

```bash
# Clone the repository
git clone https://github.com/MarlinZH/Notion_Database_to_Calendar.git
cd Notion_Database_to_Calendar

# Install dependencies
pip install -r Requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials
```

### Basic Usage

```bash
# Test with dry-run (no changes made)
python notion_calendar_sync.py

# Perform actual sync
python notion_calendar_sync.py --no-dry-run

# Test with limited pages
python notion_calendar_sync.py --max-pages 5
```

## 📖 Documentation

- **[Quick Reference](docs/QUICK_REFERENCE.md)** - **NEW!** Guide to v2.0 features
- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed setup instructions
- **[Examples](docs/EXAMPLES.md)** - Real-world usage examples
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[API Documentation](docs/API.md)** - Internal API reference
- **[Changelog](CHANGELOG.md)** - Version history and migration guide
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines

## 🗂️ Notion Database Structure

Your Notion database needs these properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| **Tasks** | Title | Yes | Event title (changed from "Name" in v2.0) |
| **Date** | Date | Conditional* | Specific date for one-time events |
| **Day of the Week** | Multi-select | Conditional* | Days for recurring events (1-Monday, 2-Tuesday, etc.) |
| **Time Slot** | Text | Conditional* | Time in HHMM format (e.g., "0630") |
| **Duration** | Number | No | Duration in minutes (defaults to 60) |
| **Priority** | Select | No | High/Medium/Low for color coding |
| **Frequency** | Select | No | Daily/Weekly/Bi-Weekly/Monthly/Bi-Monthly (defaults to Weekly) |
| **Google Event ID** | Rich Text | No | Auto-populated by script |

*Either "Date" OR both "Day of the Week" and "Time Slot" are required.

### Example Entries

**One-time event:**
```
Tasks: "Doctor's Appointment"
Date: October 25, 2025, 2:00 PM
Duration: 60
Priority: High
```

**Daily routine:**
```
Tasks: "Morning Meditation"
Time Slot: 0600
Duration: 30
Frequency: Daily
Priority: High
```

**Weekly recurring:**
```
Tasks: "Team Meeting"
Day of the Week: 1-Monday, 3-Wednesday, 5-Friday
Time Slot: 0930
Duration: 60
Frequency: Weekly
Priority: Medium
```

**Monthly review:**
```
Tasks: "Monthly Budget Review"
Day of the Week: 7-Sunday
Time Slot: 1400
Duration: 120
Frequency: Monthly
Priority: High
```

## 🎯 Use Cases

- **📚 Students:** Sync class schedules and assignment due dates
- **💼 Professionals:** Manage recurring meetings and deadlines
- **🏋️ Fitness Enthusiasts:** Track workout routines with custom durations
- **✍️ Content Creators:** Plan publication schedules with priority colors
- **👥 Teams:** Coordinate shared calendars from Notion databases
- **🧘 Personal Development:** Daily habits and routines with flexible frequencies

## 🔧 Configuration

Create a `.env` file with:

```env
NOTION_API_KEY=secret_your_notion_token
NOTION_DATABASE_ID=your_database_id
GOOGLE_APPLICATION_CREDENTIALS=GOOGLE_SERVICE_ACCOUNT.json
GOOGLE_CALENDAR_ID=primary
TIMEZONE=America/New_York
```

See [Setup Guide](docs/SETUP_GUIDE.md) for detailed configuration steps.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Notion API](https://developers.notion.com/)
- [Google Calendar API](https://developers.google.com/calendar)
- All contributors who have helped improve this project

## 📊 Project Stats

- **Language:** Python 3.8+
- **Version:** 2.0.0
- **Dependencies:** 5 packages
- **Tests:** Basic unit tests included
- **CI/CD:** GitHub Actions

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature idea? Please [open an issue](https://github.com/MarlinZH/Notion_Database_to_Calendar/issues)!

## 💬 Support

Need help? Check:
1. [Quick Reference Guide](docs/QUICK_REFERENCE.md) - **Start here for v2.0 features!**
2. [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
3. [Existing Issues](https://github.com/MarlinZH/Notion_Database_to_Calendar/issues)
4. Open a new issue with details

## 🗺️ Roadmap

- [x] Duration support (v2.0)
- [x] Multiple frequency options (v2.0)
- [x] Priority-based colors (v2.0)
- [ ] Two-way sync (Calendar → Notion)
- [ ] Web interface for configuration
- [ ] Multiple database support
- [ ] Reminder notifications
- [ ] Docker containerization
- [ ] Event deletion sync
- [ ] Conflict resolution

## 📈 Version History

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

### Recent Updates

**v2.0.0** (2025-12-10)
- Added Duration support for custom event lengths
- Implemented Frequency-based recurring events (Daily/Weekly/Bi-Weekly/Monthly/Bi-Monthly)
- Added Priority-based color coding (High=Red, Medium=Yellow, Low=Green)
- Changed title property from "Name" to "Tasks"
- Enhanced logging and error handling

**v1.0.0** (2024-10-24)
- Initial release with basic Notion to Google Calendar sync

---

**Made with ❤️ by the community**

If this project helps you, please give it a ⭐!
