/**
 * blockly/generators/arduino_generator.js
 * C++ code generators for:
 *   - All custom Arduino blocks
 *   - Blockly built-in blocks used from Logic / Math categories
 */

const ArduinoGenerator = new Blockly.CodeGenerator('Arduino');

// ── Operator precedence (mirrors C++ precedence levels) ─────────────────────
ArduinoGenerator.ORDER_ATOMIC        = 0;   // literals, identifiers
ArduinoGenerator.ORDER_UNARY_PLUS    = 3;   // unary +, !, ~
ArduinoGenerator.ORDER_LOGICAL_NOT   = 3;
ArduinoGenerator.ORDER_MULTIPLICATION = 5;
ArduinoGenerator.ORDER_DIVISION      = 5;
ArduinoGenerator.ORDER_MODULUS       = 5;
ArduinoGenerator.ORDER_ADDITION      = 6;
ArduinoGenerator.ORDER_SUBTRACTION   = 6;
ArduinoGenerator.ORDER_RELATIONAL    = 9;   // <, >, <=, >=
ArduinoGenerator.ORDER_EQUALITY      = 10;  // ==, !=
ArduinoGenerator.ORDER_LOGICAL_AND   = 13;  // &&
ArduinoGenerator.ORDER_LOGICAL_OR    = 14;  // ||
ArduinoGenerator.ORDER_NONE          = 99;

// ════════════════════════════════════════════════════════════════════════════
// STRUCTURE
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_setup_loop'] = function (block, generator) {
  var setupCode = generator.statementToCode(block, 'SETUP');
  var loopCode  = generator.statementToCode(block, 'LOOP');
  return (
    'void setup() {\n' + setupCode + '}\n\n' +
    'void loop() {\n'  + loopCode  + '}\n'
  );
};

// ════════════════════════════════════════════════════════════════════════════
// DIGITAL I/O
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_pinmode'] = function (block, generator) {
  var pin  = block.getFieldValue('PIN');
  var mode = block.getFieldValue('MODE');
  return 'pinMode(' + pin + ', ' + mode + ');\n';
};

ArduinoGenerator.forBlock['arduino_digitalwrite'] = function (block, generator) {
  var pin   = block.getFieldValue('PIN');
  var value = block.getFieldValue('VALUE');
  return 'digitalWrite(' + pin + ', ' + value + ');\n';
};

// Expression block: plug into if-condition or compare block
ArduinoGenerator.forBlock['arduino_digitalread'] = function (block, generator) {
  var pin = block.getFieldValue('PIN');
  return ['digitalRead(' + pin + ')', ArduinoGenerator.ORDER_ATOMIC];
};

// ════════════════════════════════════════════════════════════════════════════
// ANALOG I/O
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_analogread'] = function (block, generator) {
  var pin = block.getFieldValue('PIN');
  return ['analogRead(A' + pin + ')', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_analogwrite'] = function (block, generator) {
  var pin   = block.getFieldValue('PIN');
  var value = generator.valueToCode(block, 'VALUE', ArduinoGenerator.ORDER_NONE) || '0';
  return 'analogWrite(' + pin + ', ' + value + ');\n';
};

ArduinoGenerator.forBlock['arduino_map'] = function (block, generator) {
  var val      = block.getFieldValue('VAL');
  var fromLow  = block.getFieldValue('FROM_LOW');
  var fromHigh = block.getFieldValue('FROM_HIGH');
  var toLow    = block.getFieldValue('TO_LOW');
  var toHigh   = block.getFieldValue('TO_HIGH');
  return [
    'map(' + val + ', ' + fromLow + ', ' + fromHigh + ', ' + toLow + ', ' + toHigh + ')',
    ArduinoGenerator.ORDER_ATOMIC
  ];
};

// ════════════════════════════════════════════════════════════════════════════
// TIME
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_delay'] = function (block, generator) {
  var ms = block.getFieldValue('MS');
  return 'delay(' + ms + ');\n';
};

ArduinoGenerator.forBlock['arduino_delay_microseconds'] = function (block, generator) {
  var us = block.getFieldValue('US');
  return 'delayMicroseconds(' + us + ');\n';
};

ArduinoGenerator.forBlock['arduino_millis'] = function (block, generator) {
  return ['millis()', ArduinoGenerator.ORDER_ATOMIC];
};

// ════════════════════════════════════════════════════════════════════════════
// VARIABLES (custom Arduino typed declarations)
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_variable_int'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var value = block.getFieldValue('VALUE');
  return 'int ' + name + ' = ' + value + ';\n';
};

// int name = [expression block]  e.g. int val = digitalRead(2);
ArduinoGenerator.forBlock['arduino_variable_int_expr'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var value = generator.valueToCode(block, 'VALUE', ArduinoGenerator.ORDER_NONE) || '0';
  return 'int ' + name + ' = ' + value + ';\n';
};

// name = [expression block]  e.g. val = analogRead(A0);
ArduinoGenerator.forBlock['arduino_variable_assign'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var value = generator.valueToCode(block, 'VALUE', ArduinoGenerator.ORDER_NONE) || '0';
  return name + ' = ' + value + ';\n';
};

ArduinoGenerator.forBlock['arduino_variable_bool'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var value = block.getFieldValue('VALUE');
  return 'bool ' + name + ' = ' + value + ';\n';
};

// ════════════════════════════════════════════════════════════════════════════
// SERIAL
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_serial_begin'] = function (block, generator) {
  return 'Serial.begin(' + block.getFieldValue('BAUD') + ');\n';
};

ArduinoGenerator.forBlock['arduino_serial_print'] = function (block, generator) {
  return 'Serial.print("' + block.getFieldValue('VALUE') + '");\n';
};

ArduinoGenerator.forBlock['arduino_serial_println'] = function (block, generator) {
  return 'Serial.println("' + block.getFieldValue('VALUE') + '");\n';
};

// ════════════════════════════════════════════════════════════════════════════
// BUILT-IN BLOCKLY: LOGIC
// These are standard Blockly blocks (controls_if, logic_compare, etc.)
// We only need to define the C++ generator, Blockly already has the visuals.
// ════════════════════════════════════════════════════════════════════════════

// if / if-else / else-if
ArduinoGenerator.forBlock['controls_if'] = function (block, generator) {
  var n    = 0;
  var code = '';
  do {
    var condition = generator.valueToCode(block, 'IF' + n, ArduinoGenerator.ORDER_NONE) || 'false';
    var branch    = generator.statementToCode(block, 'DO' + n);
    code += (n === 0 ? 'if' : ' else if') + ' (' + condition + ') {\n' + branch + '}';
    n++;
  } while (block.getInput('IF' + n));
  if (block.getInput('ELSE')) {
    code += ' else {\n' + generator.statementToCode(block, 'ELSE') + '}';
  }
  return code + '\n';
};

// Comparison: ==, !=, <, <=, >, >=
ArduinoGenerator.forBlock['logic_compare'] = function (block, generator) {
  var OPS = { EQ: '==', NEQ: '!=', LT: '<', LTE: '<=', GT: '>', GTE: '>=' };
  var op  = OPS[block.getFieldValue('OP')];
  var a   = generator.valueToCode(block, 'A', ArduinoGenerator.ORDER_RELATIONAL) || '0';
  var b   = generator.valueToCode(block, 'B', ArduinoGenerator.ORDER_RELATIONAL) || '0';
  return [a + ' ' + op + ' ' + b, ArduinoGenerator.ORDER_EQUALITY];
};

// AND / OR
ArduinoGenerator.forBlock['logic_operation'] = function (block, generator) {
  var op   = block.getFieldValue('OP') === 'AND' ? '&&' : '||';
  var order = block.getFieldValue('OP') === 'AND'
    ? ArduinoGenerator.ORDER_LOGICAL_AND
    : ArduinoGenerator.ORDER_LOGICAL_OR;
  var a = generator.valueToCode(block, 'A', order) || 'false';
  var b = generator.valueToCode(block, 'B', order) || 'false';
  return [a + ' ' + op + ' ' + b, order];
};

// NOT
ArduinoGenerator.forBlock['logic_negate'] = function (block, generator) {
  var val = generator.valueToCode(block, 'BOOL', ArduinoGenerator.ORDER_LOGICAL_NOT) || 'false';
  return ['!' + val, ArduinoGenerator.ORDER_LOGICAL_NOT];
};

// true / false literal
ArduinoGenerator.forBlock['logic_boolean'] = function (block, generator) {
  return [block.getFieldValue('BOOL') === 'TRUE' ? 'true' : 'false', ArduinoGenerator.ORDER_ATOMIC];
};

// ════════════════════════════════════════════════════════════════════════════
// BUILT-IN BLOCKLY: LOOPS
// ════════════════════════════════════════════════════════════════════════════

// while loop (controls_whileUntil)
ArduinoGenerator.forBlock['controls_whileUntil'] = function (block, generator) {
  var isUntil   = block.getFieldValue('MODE') === 'UNTIL';
  var condition = generator.valueToCode(block, 'BOOL', ArduinoGenerator.ORDER_LOGICAL_NOT) || 'false';
  var branch    = generator.statementToCode(block, 'DO');
  if (isUntil) condition = '!' + condition;
  return 'while (' + condition + ') {\n' + branch + '}\n';
};

// for loop (controls_for)
ArduinoGenerator.forBlock['controls_for'] = function (block, generator) {
  var varName = generator.nameDB_
    ? generator.nameDB_.getName(block.getFieldValue('VAR'), Blockly.Names.NameType.VARIABLE)
    : block.getFieldValue('VAR');
  var from   = generator.valueToCode(block, 'FROM', ArduinoGenerator.ORDER_NONE) || '0';
  var to     = generator.valueToCode(block, 'TO',   ArduinoGenerator.ORDER_NONE) || '0';
  var by     = generator.valueToCode(block, 'BY',   ArduinoGenerator.ORDER_NONE) || '1';
  var branch = generator.statementToCode(block, 'DO');
  return (
    'for (int ' + varName + ' = ' + from + '; ' +
    varName + ' <= ' + to + '; ' +
    varName + ' += ' + by + ') {\n' + branch + '}\n'
  );
};

// ════════════════════════════════════════════════════════════════════════════
// BUILT-IN BLOCKLY: MATH
// ════════════════════════════════════════════════════════════════════════════

// Number literal
ArduinoGenerator.forBlock['math_number'] = function (block, generator) {
  var num = parseFloat(block.getFieldValue('NUM'));
  return [String(num), ArduinoGenerator.ORDER_ATOMIC];
};

// Arithmetic: +, -, *, /
ArduinoGenerator.forBlock['math_arithmetic'] = function (block, generator) {
  var OPS = {
    ADD:      ['+', ArduinoGenerator.ORDER_ADDITION],
    MINUS:    ['-', ArduinoGenerator.ORDER_SUBTRACTION],
    MULTIPLY: ['*', ArduinoGenerator.ORDER_MULTIPLICATION],
    DIVIDE:   ['/', ArduinoGenerator.ORDER_DIVISION],
    POWER:    ['**', ArduinoGenerator.ORDER_NONE],
  };
  var tuple = OPS[block.getFieldValue('OP')];
  var op    = tuple[0];
  var order = tuple[1];
  var a     = generator.valueToCode(block, 'A', order) || '0';
  var b     = generator.valueToCode(block, 'B', order) || '0';
  return [a + ' ' + op + ' ' + b, order];
};

// ════════════════════════════════════════════════════════════════════════════
// SERIAL — EXTRA
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_serial_print_expr'] = function (block, generator) {
  var value = generator.valueToCode(block, 'VALUE', ArduinoGenerator.ORDER_NONE) || '0';
  return 'Serial.print(' + value + ');\n';
};

ArduinoGenerator.forBlock['arduino_serial_println_expr'] = function (block, generator) {
  var value = generator.valueToCode(block, 'VALUE', ArduinoGenerator.ORDER_NONE) || '0';
  return 'Serial.println(' + value + ');\n';
};

ArduinoGenerator.forBlock['arduino_serial_available'] = function (block, generator) {
  return ['Serial.available()', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_serial_read'] = function (block, generator) {
  return ['Serial.read()', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_serial_flush'] = function (block, generator) {
  return 'Serial.flush();\n';
};

// ════════════════════════════════════════════════════════════════════════════
// DIGITAL I/O — EXTRA
// ════════════════════════════════════════════════════════════════════════════

// Toggle uses digitalRead then digitalWrite with the inverted value
ArduinoGenerator.forBlock['arduino_pin_toggle'] = function (block, generator) {
  var pin = block.getFieldValue('PIN');
  return 'digitalWrite(' + pin + ', !digitalRead(' + pin + '));\n';
};

// ════════════════════════════════════════════════════════════════════════════
// ANALOG I/O — EXTRA
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_constrain'] = function (block, generator) {
  var val = generator.valueToCode(block, 'VAL', ArduinoGenerator.ORDER_NONE) || '0';
  var min = generator.valueToCode(block, 'MIN', ArduinoGenerator.ORDER_NONE) || '0';
  var max = generator.valueToCode(block, 'MAX', ArduinoGenerator.ORDER_NONE) || '255';
  return ['constrain(' + val + ', ' + min + ', ' + max + ')', ArduinoGenerator.ORDER_ATOMIC];
};

// ════════════════════════════════════════════════════════════════════════════
// VARIABLES — EXTRA
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_variable_float'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var value = block.getFieldValue('VALUE');
  return 'float ' + name + ' = ' + value + ';\n';
};

ArduinoGenerator.forBlock['arduino_variable_string'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var value = block.getFieldValue('VALUE');
  return 'String ' + name + ' = "' + value + '";\n';
};

ArduinoGenerator.forBlock['arduino_variable_get'] = function (block, generator) {
  var name = block.getFieldValue('NAME');
  return [name, ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_variable_compound'] = function (block, generator) {
  var name  = block.getFieldValue('NAME');
  var op    = block.getFieldValue('OP');
  var value = block.getFieldValue('VALUE');
  if (op === '= 0') return name + ' = 0;\n';
  return name + ' ' + op + ' ' + value + ';\n';
};

// ════════════════════════════════════════════════════════════════════════════
// MATH — EXTRA
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_math_modulo'] = function (block, generator) {
  var a = generator.valueToCode(block, 'A', ArduinoGenerator.ORDER_MODULUS) || '0';
  var b = generator.valueToCode(block, 'B', ArduinoGenerator.ORDER_MODULUS) || '1';
  return [a + ' % ' + b, ArduinoGenerator.ORDER_MODULUS];
};

ArduinoGenerator.forBlock['arduino_math_abs'] = function (block, generator) {
  var val = generator.valueToCode(block, 'VALUE', ArduinoGenerator.ORDER_NONE) || '0';
  return ['abs(' + val + ')', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_math_sqrt'] = function (block, generator) {
  var val = generator.valueToCode(block, 'VALUE', ArduinoGenerator.ORDER_NONE) || '0';
  return ['sqrt(' + val + ')', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_math_pow'] = function (block, generator) {
  var base = generator.valueToCode(block, 'BASE', ArduinoGenerator.ORDER_NONE) || '0';
  var exp  = generator.valueToCode(block, 'EXP',  ArduinoGenerator.ORDER_NONE) || '2';
  return ['pow(' + base + ', ' + exp + ')', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_math_random'] = function (block, generator) {
  var min = block.getFieldValue('MIN');
  var max = block.getFieldValue('MAX');
  return ['random(' + min + ', ' + max + ')', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_math_round'] = function (block, generator) {
  var val = generator.valueToCode(block, 'VALUE', ArduinoGenerator.ORDER_NONE) || '0';
  return ['round(' + val + ')', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_math_min'] = function (block, generator) {
  var a = generator.valueToCode(block, 'A', ArduinoGenerator.ORDER_NONE) || '0';
  var b = generator.valueToCode(block, 'B', ArduinoGenerator.ORDER_NONE) || '0';
  return ['min(' + a + ', ' + b + ')', ArduinoGenerator.ORDER_ATOMIC];
};

ArduinoGenerator.forBlock['arduino_math_max'] = function (block, generator) {
  var a = generator.valueToCode(block, 'A', ArduinoGenerator.ORDER_NONE) || '0';
  var b = generator.valueToCode(block, 'B', ArduinoGenerator.ORDER_NONE) || '0';
  return ['max(' + a + ', ' + b + ')', ArduinoGenerator.ORDER_ATOMIC];
};

// ════════════════════════════════════════════════════════════════════════════
// LOOPS — EXTRA
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_break'] = function (block, generator) {
  return 'break;\n';
};

ArduinoGenerator.forBlock['arduino_continue'] = function (block, generator) {
  return 'continue;\n';
};

ArduinoGenerator.forBlock['arduino_do_while'] = function (block, generator) {
  var branch    = generator.statementToCode(block, 'DO');
  var condition = generator.valueToCode(block, 'CONDITION', ArduinoGenerator.ORDER_NONE) || 'false';
  return 'do {\n' + branch + '} while (' + condition + ');\n';
};

// ════════════════════════════════════════════════════════════════════════════
// TIME — EXTRA
// ════════════════════════════════════════════════════════════════════════════

ArduinoGenerator.forBlock['arduino_micros'] = function (block, generator) {
  return ['micros()', ArduinoGenerator.ORDER_ATOMIC];
};

// ════════════════════════════════════════════════════════════════════════════
// LED HELPERS
// ════════════════════════════════════════════════════════════════════════════

// Expands to a for-loop that blinks the LED N times
ArduinoGenerator.forBlock['arduino_led_blink'] = function (block, generator) {
  var pin   = block.getFieldValue('PIN');
  var times = block.getFieldValue('TIMES');
  var ms    = block.getFieldValue('MS');
  return (
    'for (int _i = 0; _i < ' + times + '; _i++) {\n' +
    '  digitalWrite(' + pin + ', HIGH);\n' +
    '  delay(' + ms + ');\n' +
    '  digitalWrite(' + pin + ', LOW);\n' +
    '  delay(' + ms + ');\n' +
    '}\n'
  );
};

// ════════════════════════════════════════════════════════════════════════════
// BUTTON & INPUT HELPERS
// ════════════════════════════════════════════════════════════════════════════

// Active-LOW button: LOW means pressed when using INPUT_PULLUP
ArduinoGenerator.forBlock['arduino_button_pressed'] = function (block, generator) {
  var pin = block.getFieldValue('PIN');
  return ['(digitalRead(' + pin + ') == LOW)', ArduinoGenerator.ORDER_EQUALITY];
};

