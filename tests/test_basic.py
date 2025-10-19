#!/usr/bin/env python3
"""
Basic tests for Notion Database to Calendar sync.

Note: These are basic unit tests. For full integration testing,
you'll need actual Notion and Google Calendar credentials.
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notion_calendar_sync import (
    parse_time_slot,
    extract_title,
    DAY_MAP,
)


class TestTimeSlotParsing(unittest.TestCase):
    """Test time slot parsing functionality."""
    
    def test_valid_time_formats(self):
        """Test valid HHMM formats."""
        self.assertEqual(parse_time_slot("0600"), (6, 0))
        self.assertEqual(parse_time_slot("1330"), (13, 30))
        self.assertEqual(parse_time_slot("2359"), (23, 59))
        self.assertEqual(parse_time_slot("0000"), (0, 0))
    
    def test_invalid_time_formats(self):
        """Test invalid time formats raise errors."""
        with self.assertRaises(ValueError):
            parse_time_slot("600")  # Too short
        
        with self.assertRaises(ValueError):
            parse_time_slot("06:00")  # Wrong format
        
        with self.assertRaises(ValueError):
            parse_time_slot("2400")  # Invalid hour
        
        with self.assertRaises(ValueError):
            parse_time_slot("1260")  # Invalid minute
        
        with self.assertRaises(ValueError):
            parse_time_slot("abcd")  # Not a number


class TestTitleExtraction(unittest.TestCase):
    """Test title extraction from Notion pages."""
    
    def test_extract_title_with_plain_text(self):
        """Test extracting title with plain_text."""
        page = {
            "properties": {
                "Name": {
                    "title": [
                        {"plain_text": "Test Event"}
                    ]
                }
            }
        }
        self.assertEqual(extract_title(page), "Test Event")
    
    def test_extract_title_with_text_content(self):
        """Test extracting title with text.content."""
        page = {
            "properties": {
                "Name": {
                    "title": [
                        {"text": {"content": "Another Event"}}
                    ]
                }
            }
        }
        self.assertEqual(extract_title(page), "Another Event")
    
    def test_extract_title_no_property(self):
        """Test extracting title when property is missing."""
        page = {"properties": {}}
        self.assertEqual(extract_title(page), "(no title property)")
    
    def test_extract_title_empty(self):
        """Test extracting empty title."""
        page = {
            "properties": {
                "Name": {"title": []}
            }
        }
        self.assertEqual(extract_title(page), "(untitled)")


class TestDayMapping(unittest.TestCase):
    """Test weekday mapping."""
    
    def test_day_map_completeness(self):
        """Test that all weekdays are mapped."""
        expected_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.assertEqual(sorted(DAY_MAP.keys()), sorted(expected_days))
    
    def test_day_map_values(self):
        """Test that day mappings are correct."""
        self.assertEqual(DAY_MAP["Monday"], 0)
        self.assertEqual(DAY_MAP["Tuesday"], 1)
        self.assertEqual(DAY_MAP["Wednesday"], 2)
        self.assertEqual(DAY_MAP["Thursday"], 3)
        self.assertEqual(DAY_MAP["Friday"], 4)
        self.assertEqual(DAY_MAP["Saturday"], 5)
        self.assertEqual(DAY_MAP["Sunday"], 6)


class TestEventPayloadBuilding(unittest.TestCase):
    """Test event payload building."""
    
    def test_all_day_event(self):
        """Test building payload for all-day event."""
        # This would need the actual function imported
        # Placeholder for now
        pass
    
    def test_timed_event(self):
        """Test building payload for timed event."""
        # This would need the actual function imported
        # Placeholder for now
        pass


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
