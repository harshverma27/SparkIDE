"""Tests for the QWebChannel bridge (bridge/channel.py)."""

import json
from unittest.mock import Mock

from bridge.channel import Bridge


def test_on_code_update_emits_code_changed(qapp):
    bridge = Bridge()
    received = []
    bridge.code_changed.connect(received.append)

    bridge.on_code_update("void setup() {}")

    assert received == ["void setup() {}"]


def test_on_block_count_update_emits_block_count_changed(qapp):
    bridge = Bridge()
    received = []
    bridge.block_count_changed.connect(received.append)

    bridge.on_block_count_update(7)

    assert received == [7]


def test_load_workspace_calls_page_with_double_encoded_json(qapp):
    bridge = Bridge()
    page = Mock()
    bridge.set_page(page)

    workspace_json = '{"blocks": []}'
    bridge.load_workspace(workspace_json)

    page.runJavaScript.assert_called_once()
    script = page.runJavaScript.call_args.args[0]
    # The JSON string is double-encoded so it is a safe JS string literal.
    expected = f"window.loadWorkspace({json.dumps(workspace_json)});"
    assert script == expected


def test_load_workspace_without_page_is_a_noop(qapp):
    bridge = Bridge()
    # No set_page() call — must not raise.
    bridge.load_workspace('{"blocks": []}')


def test_get_workspace_json_passes_callback_to_page(qapp):
    bridge = Bridge()
    page = Mock()
    bridge.set_page(page)
    callback = Mock()

    bridge.get_workspace_json(callback)

    page.runJavaScript.assert_called_once_with("window.getWorkspaceJson();", callback)
