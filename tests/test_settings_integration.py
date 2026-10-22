#!/usr/bin/env python3
"""Paired historical preservation oracle and strict current production gate."""
from frontend_history_support import paired_suite, main


def load_tests(loader, tests, pattern):
    return paired_suite("test_settings_integration.py")


if __name__ == '__main__':
    main("test_settings_integration.py")
