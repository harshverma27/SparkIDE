from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BLOCKS_JS = ROOT / "blockly" / "blocks" / "arduino_blocks.js"
GENERATOR_JS = ROOT / "blockly" / "generators" / "arduino_generator.js"
INDEX_HTML = ROOT / "blockly" / "index.html"


def test_blockly_runtime_uses_local_assets():
    html = INDEX_HTML.read_text()

    assert "https://unpkg.com" not in html
    assert "vendor/blockly_compressed.js" in html
    assert "vendor/blocks_compressed.js" in html
    assert "vendor/en.js" in html


def test_custom_blocks_have_generators():
    blocks_js = BLOCKS_JS.read_text()
    generator_js = GENERATOR_JS.read_text()

    block_types = set(re.findall(r"Blockly\.Blocks\['([^']+)'\]", blocks_js))
    generator_types = set(re.findall(r"ArduinoGenerator\.forBlock\['([^']+)'\]", generator_js))

    assert block_types
    assert block_types - generator_types == set()


def test_toolbox_references_existing_blocks():
    html = INDEX_HTML.read_text()
    blocks_js = BLOCKS_JS.read_text()

    toolbox_types = set(re.findall(r"type: '([^']+)'", html))
    custom_block_types = set(re.findall(r"Blockly\.Blocks\['([^']+)'\]", blocks_js))
    built_in_types = {
        "controls_if",
        "controls_whileUntil",
        "controls_for",
        "logic_compare",
        "logic_operation",
        "logic_negate",
        "logic_boolean",
        "math_number",
        "math_arithmetic",
    }

    assert toolbox_types - custom_block_types - built_in_types == set()


def test_generator_does_not_emit_python_style_power_operator():
    generator_js = GENERATOR_JS.read_text()

    assert "'**'" not in generator_js
    assert "pow(" in generator_js
