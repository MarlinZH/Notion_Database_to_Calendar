# Notion Database to Calendar

[![Run Tests](https://github.com/MarlinZH/Notion_Database_to_Calendar/workflows/Run%20Tests/badge.svg)](https://github.com/MarlinZH/Notion_Database_to_Calendar/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A powerful automation tool that syncs your Notion database tasks to Google Calendar, enabling seamless planning and scheduling across platforms.

## ✨ Features

- **🔄 One-Way Sync:** Notion → Google Calendar
- **📅 Flexible Scheduling:**
  - Single events with specific dates
  - Recurring events based on day of week and time
- **🛡️ Safe Testing:** Dry-run mode to preview changes
- **🔍 Smart Deduplication:** Prevents duplicate events
- **⚡ Batch Processing:** Handles large databases with pagination
- **🔧 Error Handling:** Comprehensive validation and error reporting
- **📊 Progress Tracking:** Detailed logging and sync statistics

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
pip install -r requirements.txt

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

- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed setup instructions
- **[Examples](docs/EXAMPLES.md)** - Real-world usage examples
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[API Documentation](docs/API.md)** - Internal API reference
- **[Contributing](CONTRIBUTING.md)** - Contribution guidelines

## 🗂️ Notion Database Structure

Your Notion database needs these properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| **Name** | Title | Yes | Event title |
| **Date** | Date | Conditional* | Specific date for one-time events |
| **Day of the Week** | Multi-select | Conditional* | Days for recurring events |
| **Time Slot** | Text | Conditional* | Time in HHMM format (e.g., "0600") |
| **Google Event ID** | Rich Text | No | Auto-populated by script |

*Either "Date" OR both "Day of the Week" and "Time Slot" are required.

### Example Entries

**One-time event:**
```
Name: "Doctor's Appointment"
Date: October 25, 2025, 2:00 PM
```

**Recurring event:**
```
Name: "Morning Workout"
Day of the Week: 1-Monday, 3-Wednesday, 5-Friday
Time Slot: 0630
```

## 🎯 Use Cases

- **📚 Students:** Sync class schedules and assignment due dates
- **💼 Professionals:** Manage recurring meetings and deadlines
- **🏋️ Fitness Enthusiasts:** Track workout routines
- **✍️ Content Creators:** Plan publication schedules
- **👥 Teams:** Coordinate shared calendars from Notion databases

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
- **Dependencies:** 7 packages
- **Tests:** Basic unit tests included
- **CI/CD:** GitHub Actions

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature idea? Please [open an issue](https://github.com/MarlinZH/Notion_Database_to_Calendar/issues)!

## 💬 Support

Need help? Check:
1. [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. [Existing Issues](https://github.com/MarlinZH/Notion_Database_to_Calendar/issues)
3. Open a new issue with details

## 🗺️ Roadmap

- [ ] Two-way sync (Calendar → Notion)
- [ ] Web interface for configuration
- [ ] Multiple database support
- [ ] Event categories and colors
- [ ] Reminder notifications
- [ ] Docker containerization
- [ ] Event deletion sync
- [ ] Conflict resolution

## 📈 Version History

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

---

**Made with ❤️ by the community**

If this project helps you, please give it a ⭐!
