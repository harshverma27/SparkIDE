/**
 * tests/generate_code.js — headless code-generation CLI.
 * Usage: node tests/generate_code.js < workspace.json
 * Reads Blockly workspace-serialization JSON on stdin and prints the generated
 * Arduino C++ on stdout. Thin wrapper over tests/blockly_harness.js; used by
 * tests/test_function_blocks.py.
 */
'use strict';

const fs = require('fs');
const { generateFromWorkspace } = require('./blockly_harness.js');

const json = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(generateFromWorkspace(json));
