import io
import json
from unittest.mock import Mock, patch

from cli.arduino_cli import ArduinoCLI, ArduinoCLIError


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


def test_parse_error_handles_missing_semicolon():
    raw = "sketch.ino:9:1: error: expected ';' before 'delay' token"

    message = ArduinoCLI()._parse_error(raw)

    assert message == "The generated code is missing a semicolon before 'delay'."


def test_run_json_raises_when_cli_unavailable():
    with patch("cli.arduino_cli.shutil.which", return_value=None):
        try:
            ArduinoCLI().list_boards()
        except ArduinoCLIError as exc:
            assert "not found" in str(exc)
        else:
            raise AssertionError("expected ArduinoCLIError")


def test_compile_builds_expected_command():
    cli = ArduinoCLI()
    with patch.object(cli, "_run_streaming", return_value=True) as run:
        result = cli.compile("arduino:avr:uno", "/tmp/sketch", callback=Mock())

    assert result is True
    run.assert_called_once()
    args = run.call_args.args[0]
    assert args == ["compile", "--fqbn", "arduino:avr:uno", "/tmp/sketch"]


def test_upload_builds_expected_command_with_port():
    cli = ArduinoCLI()
    with patch.object(cli, "_run_streaming", return_value=True) as run:
        cli.upload("arduino:avr:uno", "/dev/ttyACM0", "/tmp/sketch", callback=Mock())

    args = run.call_args.args[0]
    assert args == [
        "upload",
        "--fqbn",
        "arduino:avr:uno",
        "--port",
        "/dev/ttyACM0",
        "/tmp/sketch",
    ]


class _FakeProcess:
    """Minimal stand-in for subprocess.Popen used by _run_streaming."""

    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = io.StringIO(stdout)
        self.stderr = io.StringIO(stderr)
        self._returncode = returncode

    def wait(self):
        return self._returncode


def test_run_streaming_streams_output_and_succeeds():
    cli = ArduinoCLI()
    proc = _FakeProcess(stdout="Compiling...\nDone building.\n", returncode=0)
    lines = []

    with (
        patch("cli.arduino_cli.shutil.which", return_value="/usr/bin/arduino-cli"),
        patch("cli.arduino_cli.subprocess.Popen", return_value=proc),
    ):
        ok = cli._run_streaming(["compile"], lambda text, level: lines.append((level, text)))

    assert ok is True
    messages = [text for _level, text in lines]
    assert "Compiling..." in messages
    assert "Done building." in messages
    assert ("success", "Done.") in lines


def test_run_streaming_reports_parsed_error_on_failure():
    cli = ArduinoCLI()
    proc = _FakeProcess(
        stderr="sketch.ino:7:3: error: 'ledPin' was not declared in this scope\n",
        returncode=1,
    )
    lines = []

    with (
        patch("cli.arduino_cli.shutil.which", return_value="/usr/bin/arduino-cli"),
        patch("cli.arduino_cli.subprocess.Popen", return_value=proc),
    ):
        ok = cli._run_streaming(["compile"], lambda text, level: lines.append((level, text)))

    assert ok is False
    error_messages = [text for level, text in lines if level == "error"]
    assert any("Unknown name 'ledPin'" in msg for msg in error_messages)
