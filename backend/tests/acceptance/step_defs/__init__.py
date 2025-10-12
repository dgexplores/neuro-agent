"""
Step Definitions Package

This package contains pytest-bdd step definition modules.
Step definitions are automatically discovered from test_*.py files
in the parent directory.

Structure:
    backend/tests/acceptance/
    ├── features/
    │   └── migraine_diagnosis.feature   # Gherkin scenarios
    ├── step_defs/                        # Step definitions (optional organization)
    │   └── __init__.py                   # This file
    ├── test_migraine_diagnosis.py        # Main test file with step definitions
    └── conftest.py                       # Shared fixtures and configuration

Note: pytest-bdd automatically discovers step definitions from test_*.py files,
      so this directory is optional but provided for future organization.
"""

__version__ = "1.0.0"
