/**
 * blockly/generators/arduino_generator.js
 * C++ code generators for all custom Arduino blocks.
 *
 * Uses Blockly v10 CodeGenerator API.
 * ArduinoGenerator is exposed as a global so index.html can call:
 *   ArduinoGenerator.workspaceToCode(workspace)
 */

const ArduinoGenerator = new Blockly.CodeGenerator('Arduino');

// Operator precedence constants (needed for expression/value blocks)
ArduinoGenerator.ORDER_ATOMIC = 0;   // literals, identifiers
ArduinoGenerator.ORDER_NONE   = 99;  // lowest precedence / no parens needed

// Indentation used inside setup() and loop() bodies
ArduinoGenerator.INDENT = '  ';

// ── 1. arduino_setup_loop ────────────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_setup_loop'] = function (block, generator) {
  var setupCode = generator.statementToCode(block, 'SETUP');
  var loopCode  = generator.statementToCode(block, 'LOOP');
  return (
    'void setup() {\n' + setupCode + '}\n\n' +
    'void loop() {\n'  + loopCode  + '}\n'
  );
};

// ── 2. arduino_pinmode ───────────────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_pinmode'] = function (block, generator) {
  var pin  = block.getFieldValue('PIN');
  var mode = block.getFieldValue('MODE');
  return 'pinMode(' + pin + ', ' + mode + ');\n';
};

// ── 3. arduino_digitalwrite ──────────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_digitalwrite'] = function (block, generator) {
  var pin   = block.getFieldValue('PIN');
  var value = block.getFieldValue('VALUE');
  return 'digitalWrite(' + pin + ', ' + value + ');\n';
};

// ── 4. arduino_digitalread (expression block — returns [code, ORDER]) ────────
ArduinoGenerator.forBlock['arduino_digitalread'] = function (block, generator) {
  var pin = block.getFieldValue('PIN');
  return ['digitalRead(' + pin + ')', ArduinoGenerator.ORDER_ATOMIC];
};

// ── 5. arduino_delay ─────────────────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_delay'] = function (block, generator) {
  var ms = block.getFieldValue('MS');
  return 'delay(' + ms + ');\n';
};

// ── 6. arduino_variable_int ──────────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_variable_int'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var value = block.getFieldValue('VALUE');
  return 'int ' + name + ' = ' + value + ';\n';
};

// ── 7. arduino_variable_bool ─────────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_variable_bool'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var value = block.getFieldValue('VALUE');
  return 'bool ' + name + ' = ' + value + ';\n';
};

// ── 8. arduino_serial_begin ──────────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_serial_begin'] = function (block, generator) {
  var baud = block.getFieldValue('BAUD');
  return 'Serial.begin(' + baud + ');\n';
};

// ── 9. arduino_serial_print ──────────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_serial_print'] = function (block, generator) {
  var value = block.getFieldValue('VALUE');
  return 'Serial.print("' + value + '");\n';
};

// ── 10. arduino_serial_println ───────────────────────────────────────────────
ArduinoGenerator.forBlock['arduino_serial_println'] = function (block, generator) {
  var value = block.getFieldValue('VALUE');
  return 'Serial.println("' + value + '");\n';
};
