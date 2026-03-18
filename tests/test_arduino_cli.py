"""
tests/test_arduino_cli.py — Unit tests for cli/arduino_cli.py

What to test here:
  1. test_list_boards_parses_json
       - Mock subprocess output with sample arduino-cli JSON.
       - Assert list_boards() returns correctly structured list of dicts.
       - Keys to check: "fqbn", "port", "name".

  2. test_list_boards_empty
       - Mock subprocess returning empty / no-boards JSON.
       - Assert list_boards() returns [].

  3. test_compile_success
       - Mock subprocess that exits with code 0.
       - Assert compile() returns True.
       - Assert callback was called with stdout lines.

  4. test_compile_failure
       - Mock subprocess that exits with code 1 and outputs error lines.
       - Assert compile() returns False.
       - Assert callback was called with level="error" at least once.

  5. test_parse_error_readable
       - Pass in a raw arduino-cli error string.
       - Assert _parse_error() returns a simplified human-readable string.

Run with:
    cd /home/harsh/GitHub/SparkIDE
    python -m pytest tests/ -v
"""

# TODO: import pytest
# TODO: from unittest.mock import patch, MagicMock
# TODO: from cli.arduino_cli import ArduinoCLI


class TestArduinoCLI:
    # TODO: implement test methods listed above
    pass
