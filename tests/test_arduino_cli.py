import json
from unittest.mock import Mock, patch

from cli.arduino_cli import ArduinoCLI


def test_list_boards_parses_detected_ports():
    payload = {
        "detected_ports": [
            {
                "port": {"address": "/dev/ttyACM0"},
                "matching_boards": [{"name": "Arduino UNO", "fqbn": "arduino:avr:uno"}],
            }
        ]
    }
    completed = Mock(returncode=0, stdout=json.dumps(payload), stderr="")

    with (
        patch("cli.arduino_cli.shutil.which", return_value="/usr/bin/arduino-cli"),
        patch("cli.arduino_cli.subprocess.run", return_value=completed),
    ):
        boards = ArduinoCLI().list_boards()

    assert len(boards) == 1
    assert boards[0].name == "Arduino UNO"
    assert boards[0].fqbn == "arduino:avr:uno"
    assert boards[0].port == "/dev/ttyACM0"
    assert boards[0].detected is True


def test_list_installed_boards_prioritizes_common_avr_boards():
    payload = {
        "boards": [
            {"name": "Arduino Leonardo", "fqbn": "arduino:avr:leonardo"},
            {"name": "Arduino UNO", "fqbn": "arduino:avr:uno"},
            {"name": "Arduino Nano", "fqbn": "arduino:avr:nano"},
        ]
    }
    completed = Mock(returncode=0, stdout=json.dumps(payload), stderr="")

    with (
        patch("cli.arduino_cli.shutil.which", return_value="/usr/bin/arduino-cli"),
        patch("cli.arduino_cli.subprocess.run", return_value=completed),
    ):
        boards = ArduinoCLI().list_installed_boards()

    assert [board.fqbn for board in boards] == [
        "arduino:avr:uno",
        "arduino:avr:nano",
        "arduino:avr:leonardo",
    ]


def test_parse_error_returns_beginner_message():
    raw = "sketch.ino:7:3: error: 'ledPin' was not declared in this scope"

    message = ArduinoCLI()._parse_error(raw)

    assert message == "Unknown name 'ledPin'. Check the block variable or function name."
