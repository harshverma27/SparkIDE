"""Behavioral tests for user-defined function blocks (and statement chaining).

Drives the real Blockly generator headlessly via tests/generate_code.js.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "generate_code.js"

pytestmark = pytest.mark.skipif(
    shutil.which("node") is None, reason="node is required for generator tests"
)


def generate(blocks):
    workspace = {"blocks": {"languageVersion": 0, "blocks": blocks}}
    result = subprocess.run(
        ["node", str(HARNESS)],
        input=json.dumps(workspace),
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def setup_loop(setup_block=None, loop_block=None):
    block = {"type": "arduino_setup_loop", "inputs": {}}
    if setup_block:
        block["inputs"]["SETUP"] = {"block": setup_block}
    if loop_block:
        block["inputs"]["LOOP"] = {"block": loop_block}
    return block


def test_statement_chains_emit_every_block():
    code = generate(
        [
            setup_loop(
                setup_block={
                    "type": "arduino_pinmode",
                    "fields": {"PIN": 13, "MODE": "OUTPUT"},
                    "next": {
                        "block": {
                            "type": "arduino_serial_begin",
                            "fields": {"BAUD": "9600"},
                        }
                    },
                },
                loop_block={
                    "type": "arduino_pin_toggle",
                    "fields": {"PIN": 13},
                    "next": {
                        "block": {
                            "type": "arduino_delay",
                            "fields": {"MS": 500},
                        }
                    },
                },
            )
        ]
    )
    assert "pinMode(13, OUTPUT);" in code
    assert "Serial.begin(9600);" in code
    assert "digitalWrite(13, !digitalRead(13));" in code
    assert "delay(500);" in code


def test_void_function_definition_and_call():
    code = generate(
        [
            {
                "type": "procedures_defnoreturn",
                "fields": {"NAME": "blink once"},
                "inputs": {
                    "STACK": {
                        "block": {
                            "type": "arduino_digitalwrite",
                            "fields": {"PIN": 13, "VALUE": "HIGH"},
                            "next": {
                                "block": {
                                    "type": "arduino_delay",
                                    "fields": {"MS": 200},
                                }
                            },
                        }
                    }
                },
            },
            setup_loop(
                loop_block={
                    "type": "procedures_callnoreturn",
                    "extraState": {"name": "blink once"},
                }
            ),
        ]
    )
    # Name is sanitized into a C++ identifier, consistently between def and call.
    assert "void blink_once() {" in code
    assert "blink_once();" in code
    assert "digitalWrite(13, HIGH);" in code
    assert "delay(200);" in code


def test_function_with_params_and_return_value():
    code = generate(
        [
            {
                "type": "procedures_defreturn",
                "fields": {"NAME": "doubled"},
                "extraState": {"params": [{"name": "n", "id": "param_n"}]},
                "inputs": {
                    "RETURN": {
                        "block": {
                            "type": "math_arithmetic",
                            "fields": {"OP": "MULTIPLY"},
                            "inputs": {
                                "A": {
                                    "block": {
                                        "type": "arduino_variable_get",
                                        "fields": {"NAME": "n"},
                                    }
                                },
                                "B": {"block": {"type": "math_number", "fields": {"NUM": 2}}},
                            },
                        }
                    }
                },
            },
            setup_loop(
                loop_block={
                    "type": "arduino_analogwrite",
                    "fields": {"PIN": 9},
                    "inputs": {
                        "VALUE": {
                            "block": {
                                "type": "procedures_callreturn",
                                "extraState": {"name": "doubled", "params": ["n"]},
                                "inputs": {
                                    "ARG0": {
                                        "block": {
                                            "type": "math_number",
                                            "fields": {"NUM": 21},
                                        }
                                    }
                                },
                            }
                        }
                    },
                }
            ),
        ]
    )
    assert "int doubled(int n) {" in code
    assert "return n * 2;" in code
    assert "analogWrite(9, doubled(21));" in code


def test_function_definitions_emitted_before_setup_with_prototype():
    code = generate(
        [
            setup_loop(
                loop_block={
                    "type": "procedures_callnoreturn",
                    "extraState": {"name": "helper"},
                }
            ),
            {
                "type": "procedures_defnoreturn",
                "fields": {"NAME": "helper"},
            },
        ]
    )
    assert "void helper();" in code, "missing forward prototype"
    assert code.index("void helper();") < code.index("void helper() {")
    assert code.index("void helper() {") < code.index("void setup() {")


def test_if_return_block():
    code = generate(
        [
            {
                "type": "procedures_defreturn",
                "fields": {"NAME": "clamped"},
                "extraState": {"params": [{"name": "v", "id": "param_v"}]},
                "inputs": {
                    "STACK": {
                        "block": {
                            "type": "procedures_ifreturn",
                            "extraState": '<mutation value="1"></mutation>',
                            "inputs": {
                                "CONDITION": {
                                    "block": {
                                        "type": "logic_compare",
                                        "fields": {"OP": "GT"},
                                        "inputs": {
                                            "A": {
                                                "block": {
                                                    "type": "arduino_variable_get",
                                                    "fields": {"NAME": "v"},
                                                }
                                            },
                                            "B": {
                                                "block": {
                                                    "type": "math_number",
                                                    "fields": {"NUM": 255},
                                                }
                                            },
                                        },
                                    }
                                },
                                "VALUE": {"block": {"type": "math_number", "fields": {"NUM": 255}}},
                            },
                        }
                    },
                    "RETURN": {"block": {"type": "arduino_variable_get", "fields": {"NAME": "v"}}},
                },
            },
            setup_loop(),
        ]
    )
    assert "int clamped(int v) {" in code
    assert "if (v > 255) {" in code
    assert "return 255;" in code
    assert "return v;" in code


def test_toolbox_has_dynamic_functions_category():
    html = (ROOT / "blockly" / "index.html").read_text()
    assert '"PROCEDURE"' in html, "missing custom PROCEDURE toolbox category"
    assert "Functions" in html
    assert "procedure_blocks" in html, "missing procedure_blocks theme style"


def test_procedure_blocks_have_friendly_labels():
    blocks_js = (ROOT / "blockly" / "blocks" / "arduino_blocks.js").read_text()
    assert "PROCEDURES_DEFNORETURN_TITLE" in blocks_js
    assert "PROCEDURES_DEFRETURN_RETURN" in blocks_js


def test_plain_sketch_output_unchanged():
    code = generate(
        [
            setup_loop(
                setup_block={"type": "arduino_pinmode", "fields": {"PIN": 13, "MODE": "OUTPUT"}},
                loop_block={"type": "arduino_digitalwrite", "fields": {"PIN": 13, "VALUE": "HIGH"}},
            )
        ]
    )
    assert "void setup() {\n  pinMode(13, OUTPUT);\n}" in code
    assert "void loop() {\n  digitalWrite(13, HIGH);\n}" in code
