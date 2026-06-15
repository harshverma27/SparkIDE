/**
 * tests/blockly_harness.js — shared headless Blockly code-generation harness.
 *
 * Loads the vendored Blockly runtime plus the SparkIDE blocks/generator once,
 * and exposes generateFromWorkspace(json) which turns a Blockly
 * workspace-serialization object into the generated Arduino C++ string.
 *
 * Consumed by:
 *   - tests/generate_code.js      (stdin/stdout CLI used by the pytest suite)
 *   - tests/generators.test.mjs   (node:test JS unit tests)
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const Blockly = require(path.join(ROOT, 'blockly/vendor/blockly_compressed.js'));
global.Blockly = Blockly;

require(path.join(ROOT, 'blockly/vendor/blocks_compressed.js'));
Blockly.setLocale(require(path.join(ROOT, 'blockly/vendor/en.js')));
require(path.join(ROOT, 'blockly/blocks/arduino_blocks.js'));

// The generator file declares `const ArduinoGenerator`, which stays scoped to
// the eval — re-export it onto globalThis so we can reach it afterwards.
const generatorSrc = fs.readFileSync(
  path.join(ROOT, 'blockly/generators/arduino_generator.js'), 'utf8');
eval(generatorSrc + '\nglobalThis.ArduinoGenerator = ArduinoGenerator;');

// Event construction touches the DOM (XML serialization); there is none here.
Blockly.Events.disable();

// Procedure mutators build XML DOM nodes even headless; give Blockly a
// minimal DOM implementation.
class FakeElement {
  constructor(tagName) {
    this.tagName = tagName;
    this.nodeName = tagName;
    this.attributes = {};
    this.childNodes = [];
  }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) {
    return name in this.attributes ? this.attributes[name] : null;
  }
  appendChild(child) { this.childNodes.push(child); return child; }
  get firstChild() { return this.childNodes[0] || null; }
}
Blockly.utils.xml.injectDependencies({
  document: {
    createElementNS: (ns, tagName) => new FakeElement(tagName),
    createTextNode: (text) => ({ nodeType: 3, nodeValue: text, textContent: text }),
  },
  // Parses only the flat `<mutation attr="...">` strings used by legacy
  // procedure-block extraState.
  DOMParser: class {
    parseFromString(text) {
      const el = new FakeElement('mutation');
      const match = text.match(/<(\w+)([^>]*)>/);
      if (match) {
        el.tagName = el.nodeName = match[1];
        for (const attr of match[2].matchAll(/(\w+)="([^"]*)"/g)) {
          el.attributes[attr[1]] = attr[2];
        }
      }
      return { documentElement: el, getElementsByTagName: () => [] };
    }
  },
  XMLSerializer: class { serializeToString() { return ''; } },
});

/**
 * Generate Arduino C++ from a Blockly workspace-serialization object.
 * @param {object} json - the `{ blocks: { ... } }` workspace serialization.
 * @returns {string} generated C++ source.
 */
function generateFromWorkspace(json) {
  const workspace = new Blockly.Workspace();
  Blockly.serialization.workspaces.load(json, workspace);
  return globalThis.ArduinoGenerator.workspaceToCode(workspace);
}

module.exports = { generateFromWorkspace };
