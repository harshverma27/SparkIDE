/**
 * tests/generators.test.mjs — node:test unit tests for the Arduino generator.
 * Run with:  node --test tests/
 *
 * Mirrors the key assertions in tests/test_function_blocks.py, runnable
 * directly via Node without spawning a subprocess per case.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { generateFromWorkspace } = require('./blockly_harness.js');

/** Wrap top-level blocks in a workspace-serialization envelope and generate. */
function generate(blocks) {
  return generateFromWorkspace({ blocks: { languageVersion: 0, blocks } });
}

/** Build an arduino_setup_loop block with optional setup/loop stacks. */
function setupLoop(setupBlock, loopBlock) {
  const block = { type: 'arduino_setup_loop', inputs: {} };
  if (setupBlock) block.inputs.SETUP = { block: setupBlock };
  if (loopBlock) block.inputs.LOOP = { block: loopBlock };
  return block;
}

test('plain setup/loop sketch generates expected scaffolding', () => {
  const code = generate([
    setupLoop(
      { type: 'arduino_pinmode', fields: { PIN: 13, MODE: 'OUTPUT' } },
      { type: 'arduino_digitalwrite', fields: { PIN: 13, VALUE: 'HIGH' } },
    ),
  ]);
  assert.match(code, /void setup\(\) \{\n {2}pinMode\(13, OUTPUT\);\n\}/);
  assert.match(code, /void loop\(\) \{\n {2}digitalWrite\(13, HIGH\);\n\}/);
});

test('statement chains emit every block in the chain', () => {
  const code = generate([
    setupLoop(
      {
        type: 'arduino_pinmode',
        fields: { PIN: 13, MODE: 'OUTPUT' },
        next: { block: { type: 'arduino_serial_begin', fields: { BAUD: '9600' } } },
      },
      {
        type: 'arduino_pin_toggle',
        fields: { PIN: 13 },
        next: { block: { type: 'arduino_delay', fields: { MS: 500 } } },
      },
    ),
  ]);
  assert.ok(code.includes('pinMode(13, OUTPUT);'));
  assert.ok(code.includes('Serial.begin(9600);'));
  assert.ok(code.includes('digitalWrite(13, !digitalRead(13));'));
  assert.ok(code.includes('delay(500);'));
});

test('function with params and return value, plus forward prototype', () => {
  const code = generate([
    {
      type: 'procedures_defreturn',
      fields: { NAME: 'doubled' },
      extraState: { params: [{ name: 'n', id: 'param_n' }] },
      inputs: {
        RETURN: {
          block: {
            type: 'math_arithmetic',
            fields: { OP: 'MULTIPLY' },
            inputs: {
              A: { block: { type: 'arduino_variable_get', fields: { NAME: 'n' } } },
              B: { block: { type: 'math_number', fields: { NUM: 2 } } },
            },
          },
        },
      },
    },
    setupLoop(undefined, {
      type: 'arduino_analogwrite',
      fields: { PIN: 9 },
      inputs: {
        VALUE: {
          block: {
            type: 'procedures_callreturn',
            extraState: { name: 'doubled', params: ['n'] },
            inputs: { ARG0: { block: { type: 'math_number', fields: { NUM: 21 } } } },
          },
        },
      },
    }),
  ]);
  assert.ok(code.includes('int doubled(int n) {'));
  assert.ok(code.includes('return n * 2;'));
  assert.ok(code.includes('analogWrite(9, doubled(21));'));
  // Prototype emitted before the definition.
  assert.ok(code.indexOf('int doubled(int n);') < code.indexOf('int doubled(int n) {'));
});

test('if-return block produces an early return inside a function', () => {
  const code = generate([
    {
      type: 'procedures_defreturn',
      fields: { NAME: 'clamped' },
      extraState: { params: [{ name: 'v', id: 'param_v' }] },
      inputs: {
        STACK: {
          block: {
            type: 'procedures_ifreturn',
            extraState: '<mutation value="1"></mutation>',
            inputs: {
              CONDITION: {
                block: {
                  type: 'logic_compare',
                  fields: { OP: 'GT' },
                  inputs: {
                    A: { block: { type: 'arduino_variable_get', fields: { NAME: 'v' } } },
                    B: { block: { type: 'math_number', fields: { NUM: 255 } } },
                  },
                },
              },
              VALUE: { block: { type: 'math_number', fields: { NUM: 255 } } },
            },
          },
        },
        RETURN: { block: { type: 'arduino_variable_get', fields: { NAME: 'v' } } },
      },
    },
    setupLoop(),
  ]);
  assert.ok(code.includes('int clamped(int v) {'));
  assert.ok(code.includes('if (v > 255) {'));
  assert.ok(code.includes('return 255;'));
  assert.ok(code.includes('return v;'));
});
