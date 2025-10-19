# Tests

This directory contains tests for the Notion Database to Calendar sync tool.

## Running Tests

### Run all tests:
```bash
python -m unittest discover tests
```

### Run specific test file:
```bash
python tests/test_basic.py
```

### Run with verbose output:
```bash
python -m unittest discover tests -v
```

## Test Coverage

Current tests cover:
- ✅ Time slot parsing
- ✅ Title extraction
- ✅ Day mapping
- ⏳ Event payload building (TODO)
- ⏳ Integration tests (TODO)

## Adding Tests

When adding new features, please add corresponding tests:

1. Create a new test file: `test_feature_name.py`
2. Import unittest and the functions to test
3. Create test classes inheriting from `unittest.TestCase`
4. Write test methods starting with `test_`

Example:
```python
import unittest
from notion_calendar_sync import your_function

class TestYourFeature(unittest.TestCase):
    def test_something(self):
        result = your_function("input")
        self.assertEqual(result, "expected")
```

## Integration Testing

For full integration testing, you'll need:
- Test Notion workspace
- Test Google Calendar
- Valid credentials

Create a `.env.test` file for test credentials (never commit this!).

## CI/CD

Tests can be automated with GitHub Actions (see `.github/workflows/` directory).
