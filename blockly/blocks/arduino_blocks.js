/**
 * blockly/blocks/arduino_blocks.js
 * Custom Blockly block DEFINITIONS for all 10 core Arduino blocks.
 */

// ── 1. arduino_setup_loop — main program container ──────────────────────────
Blockly.Blocks['arduino_setup_loop'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('🔌  Arduino Program');
    this.appendStatementInput('SETUP')
        .setCheck(null)
        .appendField('setup()');
    this.appendStatementInput('LOOP')
        .setCheck(null)
        .appendField('loop()');
    this.setColour(120);
    this.setTooltip('The main Arduino program. Place init code in setup(), repeated code in loop().');
    this.setDeletable(false);
  }
};

// ── 2. arduino_pinmode ───────────────────────────────────────────────────────
Blockly.Blocks['arduino_pinmode'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('pinMode(')
        .appendField(new Blockly.FieldNumber(13, 0, 53), 'PIN')
        .appendField(',')
        .appendField(new Blockly.FieldDropdown([
          ['OUTPUT',       'OUTPUT'],
          ['INPUT',        'INPUT'],
          ['INPUT_PULLUP', 'INPUT_PULLUP'],
        ]), 'MODE')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(210);
    this.setTooltip('Set a pin as INPUT or OUTPUT.');
  }
};

// ── 3. arduino_digitalwrite ──────────────────────────────────────────────────
Blockly.Blocks['arduino_digitalwrite'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('digitalWrite(')
        .appendField(new Blockly.FieldNumber(13, 0, 53), 'PIN')
        .appendField(',')
        .appendField(new Blockly.FieldDropdown([
          ['HIGH', 'HIGH'],
          ['LOW',  'LOW'],
        ]), 'VALUE')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(210);
    this.setTooltip('Write HIGH (5V) or LOW (0V) to a digital pin.');
  }
};

// ── 4. arduino_digitalread ───────────────────────────────────────────────────
Blockly.Blocks['arduino_digitalread'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('digitalRead(')
        .appendField(new Blockly.FieldNumber(2, 0, 53), 'PIN')
        .appendField(')');
    this.setOutput(true, null);   // expression block — returns HIGH or LOW
    this.setColour(210);
    this.setTooltip('Read HIGH or LOW from a digital pin. Use inside an if block.');
  }
};

// ── 5. arduino_delay ─────────────────────────────────────────────────────────
Blockly.Blocks['arduino_delay'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('delay(')
        .appendField(new Blockly.FieldNumber(1000, 0), 'MS')
        .appendField('ms)');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(30);
    this.setTooltip('Pause the program for the given number of milliseconds.');
  }
};

// ── 6. arduino_variable_int ──────────────────────────────────────────────────
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
    this.setTooltip('Declare an integer variable.');
  }
};

// ── 7. arduino_variable_bool ─────────────────────────────────────────────────
Blockly.Blocks['arduino_variable_bool'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('bool')
        .appendField(new Blockly.FieldTextInput('myFlag'), 'NAME')
        .appendField('=')
        .appendField(new Blockly.FieldDropdown([
          ['false', 'false'],
          ['true',  'true'],
        ]), 'VALUE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
    this.setTooltip('Declare a boolean variable (true or false).');
  }
};

// ── 8. arduino_serial_begin ──────────────────────────────────────────────────
Blockly.Blocks['arduino_serial_begin'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Serial.begin(')
        .appendField(new Blockly.FieldDropdown([
          ['9600',   '9600'],
          ['115200', '115200'],
          ['57600',  '57600'],
          ['38400',  '38400'],
        ]), 'BAUD')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(270);
    this.setTooltip('Initialize serial communication at the given baud rate.');
  }
};

// ── 9. arduino_serial_print ──────────────────────────────────────────────────
Blockly.Blocks['arduino_serial_print'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Serial.print(')
        .appendField(new Blockly.FieldTextInput('Hello'), 'VALUE')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(270);
    this.setTooltip('Print a value to the Serial Monitor (no newline).');
  }
};

// ── 10. arduino_serial_println ───────────────────────────────────────────────
Blockly.Blocks['arduino_serial_println'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Serial.println(')
        .appendField(new Blockly.FieldTextInput('Hello'), 'VALUE')
        .appendField(')');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(270);
    this.setTooltip('Print a value to the Serial Monitor followed by a newline.');
  }
};
