/**
 * blockly/blocks/arduino_blocks.js
 * Custom Blockly block DEFINITIONS — all Arduino blocks.
 * Built-in Blockly blocks (controls_if, logic_compare, math_number, etc.)
 * are used as-is; only their generators need to be defined in arduino_generator.js.
 */

// ════════════════════════════════════════════════════════════════════════════
// STRUCTURE
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_setup_loop'] = {
  init: function () {
    this.appendDummyInput().appendField('🔌  Arduino Program');
    this.appendStatementInput('SETUP').setCheck(null).appendField('setup()');
    this.appendStatementInput('LOOP').setCheck(null).appendField('loop()');
    this.setColour(120);
    this.setTooltip('Main program structure. setup() runs once; loop() repeats forever.');
    this.setDeletable(false);
  }
};

// ════════════════════════════════════════════════════════════════════════════
// DIGITAL I/O
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_pinmode'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('pinMode(')
        .appendField(new Blockly.FieldNumber(13, 0, 53), 'PIN')
        .appendField(',')
        .appendField(new Blockly.FieldDropdown([
          ['OUTPUT', 'OUTPUT'], ['INPUT', 'INPUT'], ['INPUT_PULLUP', 'INPUT_PULLUP'],
        ]), 'MODE')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(210);
    this.setTooltip('Set a digital pin as INPUT or OUTPUT.');
  }
};

Blockly.Blocks['arduino_digitalwrite'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('digitalWrite(')
        .appendField(new Blockly.FieldNumber(13, 0, 53), 'PIN')
        .appendField(',')
        .appendField(new Blockly.FieldDropdown([
          ['HIGH', 'HIGH'], ['LOW', 'LOW'],
        ]), 'VALUE')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(210);
    this.setTooltip('Write HIGH (5V) or LOW (0V) to a digital pin.');
  }
};

// Expression block — plug this into an if-condition or compare block
Blockly.Blocks['arduino_digitalread'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('digitalRead(')
        .appendField(new Blockly.FieldNumber(2, 0, 53), 'PIN')
        .appendField(')');
    this.setOutput(true, 'Number');
    this.setColour(210);
    this.setTooltip('Read HIGH or LOW from a digital pin. Plug into an "if" or compare block.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// ANALOG I/O
// ════════════════════════════════════════════════════════════════════════════

// Expression block — returns 0-1023
Blockly.Blocks['arduino_analogread'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('analogRead( A')
        .appendField(new Blockly.FieldNumber(0, 0, 5), 'PIN')
        .appendField(')');
    this.setOutput(true, 'Number');
    this.setColour(160);
    this.setTooltip('Read analog voltage on A0–A5. Returns 0 (0V) to 1023 (5V).');
  }
};

// Statement block — PWM output, value socket accepts any expression (e.g. map(), variable)
Blockly.Blocks['arduino_analogwrite'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('analogWrite( pin')
        .appendField(new Blockly.FieldNumber(9, 0, 53), 'PIN')
        .appendField(', value');
    this.appendValueInput('VALUE')
        .setCheck('Number');
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(160);
    this.setTooltip('Write a PWM value (0–255) to a PWM-capable pin. Plug in math/map/variable blocks.');
  }
};

// Expression block — maps a value from one range to another
Blockly.Blocks['arduino_map'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('map(')
        .appendField(new Blockly.FieldNumber(0), 'VAL')
        .appendField(', from [')
        .appendField(new Blockly.FieldNumber(0), 'FROM_LOW')
        .appendField('–')
        .appendField(new Blockly.FieldNumber(1023), 'FROM_HIGH')
        .appendField('] to [')
        .appendField(new Blockly.FieldNumber(0), 'TO_LOW')
        .appendField('–')
        .appendField(new Blockly.FieldNumber(255), 'TO_HIGH')
        .appendField('])');
    this.setOutput(true, 'Number');
    this.setColour(160);
    this.setTooltip('Re-maps a number from one range to another. e.g. analogRead → PWM range.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// TIME
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_delay'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('delay(')
        .appendField(new Blockly.FieldNumber(1000, 0), 'MS')
        .appendField('ms)');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(30);
    this.setTooltip('Pause the program for N milliseconds.');
  }
};

Blockly.Blocks['arduino_delay_microseconds'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('delayMicroseconds(')
        .appendField(new Blockly.FieldNumber(100, 0), 'US')
        .appendField('µs)');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(30);
    this.setTooltip('Pause for N microseconds (useful for precise timing).');
  }
};

// Expression block — returns milliseconds since board started
Blockly.Blocks['arduino_millis'] = {
  init: function () {
    this.appendDummyInput().appendField('millis()');
    this.setOutput(true, 'Number');
    this.setColour(30);
    this.setTooltip('Returns the number of milliseconds since the board started.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// VARIABLES
// ════════════════════════════════════════════════════════════════════════════

// Fixed-value declaration: int name = 0;
Blockly.Blocks['arduino_variable_int'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('int')
        .appendField(new Blockly.FieldTextInput('myVar'), 'NAME')
        .appendField('=')
        .appendField(new Blockly.FieldNumber(0), 'VALUE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
    this.setTooltip('Declare an integer variable with a fixed number.');
  }
};

// Expression-socket declaration: int name = [any block]
// Use this to assign digitalRead(), analogRead(), millis(), etc.
Blockly.Blocks['arduino_variable_int_expr'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('int')
        .appendField(new Blockly.FieldTextInput('myVar'), 'NAME')
        .appendField('=');
    this.appendValueInput('VALUE')
        .setCheck('Number');
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
    this.setTooltip('Declare an int and assign any expression block (e.g. digitalRead, analogRead, math).');
  }
};

// Reassignment: name = [any block]   (no type keyword — variable already declared)
Blockly.Blocks['arduino_variable_assign'] = {
  init: function () {
    this.appendDummyInput()
        .appendField(new Blockly.FieldTextInput('myVar'), 'NAME')
        .appendField('=');
    this.appendValueInput('VALUE')
        .setCheck(null);
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
    this.setTooltip('Assign a new value to an already-declared variable.');
  }
};

// Fixed-value bool declaration
Blockly.Blocks['arduino_variable_bool'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('bool')
        .appendField(new Blockly.FieldTextInput('myFlag'), 'NAME')
        .appendField('=')
        .appendField(new Blockly.FieldDropdown([
          ['false', 'false'], ['true', 'true'],
        ]), 'VALUE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
    this.setTooltip('Declare a boolean variable (true/false).');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// SERIAL
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_serial_begin'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Serial.begin(')
        .appendField(new Blockly.FieldDropdown([
          ['9600', '9600'], ['115200', '115200'], ['57600', '57600'], ['38400', '38400'],
        ]), 'BAUD')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(270);
    this.setTooltip('Initialize serial communication. Call once in setup().');
  }
};

Blockly.Blocks['arduino_serial_print'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Serial.print(')
        .appendField(new Blockly.FieldTextInput('Hello'), 'VALUE')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(270);
    this.setTooltip('Print text to the Serial Monitor (no newline).');
  }
};

Blockly.Blocks['arduino_serial_println'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Serial.println(')
        .appendField(new Blockly.FieldTextInput('Hello'), 'VALUE')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(270);
    this.setTooltip('Print text to the Serial Monitor followed by a newline.');
  }
};
