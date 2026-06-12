/**
 * blockly/blocks/arduino_blocks.js
 * Custom Blockly block DEFINITIONS — all Arduino blocks.
 * Labels are written in plain English so beginners can understand them
 * without any prior Arduino or C++ knowledge.
 */

// ════════════════════════════════════════════════════════════════════════════
// FUNCTIONS — friendly labels for the built-in Blockly procedure blocks
// (this file loads after vendor/en.js, so these override the stock strings)
// ════════════════════════════════════════════════════════════════════════════

Blockly.Msg['PROCEDURES_DEFNORETURN_TITLE'] = '🔧 Make a function called';
Blockly.Msg['PROCEDURES_DEFRETURN_TITLE'] = '🔧 Make a function called';
Blockly.Msg['PROCEDURES_DEFNORETURN_PROCEDURE'] = 'do something';
Blockly.Msg['PROCEDURES_DEFRETURN_PROCEDURE'] = 'do something';
Blockly.Msg['PROCEDURES_DEFRETURN_RETURN'] = 'give back';
Blockly.Msg['PROCEDURES_BEFORE_PARAMS'] = 'using:';
Blockly.Msg['PROCEDURES_CALL_BEFORE_PARAMS'] = 'using:';
Blockly.Msg['PROCEDURES_DEFNORETURN_TOOLTIP'] =
  'Teach the Arduino a new trick! Group blocks into a function you can reuse anywhere.';
Blockly.Msg['PROCEDURES_DEFRETURN_TOOLTIP'] =
  'A function that calculates something and gives back a number.';
Blockly.Msg['PROCEDURES_CALLNORETURN_TOOLTIP'] =
  'Run the blocks inside the function "%1".';
Blockly.Msg['PROCEDURES_CALLRETURN_TOOLTIP'] =
  'Run the function "%1" and use the number it gives back.';
Blockly.Msg['PROCEDURES_IFRETURN_TOOLTIP'] =
  'If the condition is true, leave the function right away (optionally giving back a value).';

// ════════════════════════════════════════════════════════════════════════════
// STRUCTURE
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_setup_loop'] = {
  init: function () {
    this.appendDummyInput().appendField('⚡  My Arduino Program');
    this.appendStatementInput('SETUP').setCheck(null)
        .appendField('▶  Run once at start');
    this.appendStatementInput('LOOP').setCheck(null)
        .appendField('🔁  Repeat forever');
    this.setColour(140);
    this.setTooltip('"Run once at start" happens when you first power on. "Repeat forever" keeps running until you unplug it.');
    this.setDeletable(false);
  }
};

// ════════════════════════════════════════════════════════════════════════════
// DIGITAL I/O
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_pinmode'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Set pin')
        .appendField(new Blockly.FieldNumber(13, 0, 53), 'PIN')
        .appendField('as')
        .appendField(new Blockly.FieldDropdown([
          ['Output (send signal)',    'OUTPUT'],
          ['Input (read signal)',     'INPUT'],
          ['Input with Pull-up',     'INPUT_PULLUP'],
        ]), 'MODE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Tell the Arduino whether a pin will send signals out (LED) or read signals in (button/sensor). Do this once in "Run once at start".');
  }
};

Blockly.Blocks['arduino_digitalwrite'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Turn pin')
        .appendField(new Blockly.FieldNumber(13, 0, 53), 'PIN')
        .appendField(new Blockly.FieldDropdown([
          ['ON  (5V)',  'HIGH'],
          ['OFF (0V)',  'LOW'],
        ]), 'VALUE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Send power to a pin (ON = 5V = LED on) or cut it (OFF = 0V = LED off).');
  }
};

// Expression block — plug into an if-condition or variable
Blockly.Blocks['arduino_digitalread'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Read pin')
        .appendField(new Blockly.FieldNumber(2, 0, 53), 'PIN')
        .appendField('(ON or OFF ?)');
    this.setOutput(true, 'Number');
    this.setColour(185);
    this.setTooltip('Check whether a pin has power (ON/HIGH) or not (OFF/LOW). Plug into an "if" or comparison block.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// ANALOG I/O
// ════════════════════════════════════════════════════════════════════════════

// Expression block — returns 0-1023
Blockly.Blocks['arduino_analogread'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Read analog sensor on pin A')
        .appendField(new Blockly.FieldNumber(0, 0, 5), 'PIN')
        .appendField('(0 – 1023)');
    this.setOutput(true, 'Number');
    this.setColour(185);
    this.setTooltip('Reads a sensor (like a potentiometer or light sensor) and gives a number from 0 (no voltage) to 1023 (full voltage).');
  }
};

// Statement block — PWM output, value socket accepts any expression
Blockly.Blocks['arduino_analogwrite'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Set brightness of pin')
        .appendField(new Blockly.FieldNumber(9, 0, 53), 'PIN')
        .appendField('to');
    this.appendValueInput('VALUE')
        .setCheck('Number');
    this.appendDummyInput().appendField('(0 – 255)');
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Control the brightness of an LED or speed of a motor. 0 = fully off, 255 = fully on. Pin must support "~" (PWM).');
  }
};

// Expression block — maps a value from one range to another
Blockly.Blocks['arduino_map'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Scale')
        .appendField(new Blockly.FieldNumber(0), 'VAL')
        .appendField('from [')
        .appendField(new Blockly.FieldNumber(0), 'FROM_LOW')
        .appendField('–')
        .appendField(new Blockly.FieldNumber(1023), 'FROM_HIGH')
        .appendField('] to [')
        .appendField(new Blockly.FieldNumber(0), 'TO_LOW')
        .appendField('–')
        .appendField(new Blockly.FieldNumber(255), 'TO_HIGH')
        .appendField(']');
    this.setOutput(true, 'Number');
    this.setColour(185);
    this.setTooltip('Converts a number from one range into another. e.g. turn a sensor reading (0–1023) into an LED brightness (0–255).');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// TIME
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_delay'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Wait')
        .appendField(new Blockly.FieldNumber(1000, 0), 'MS')
        .appendField('milliseconds  (1000 ms = 1 second)');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(42);
    this.setTooltip('Pause the program. Nothing else happens during this wait. 1000 ms = 1 second.');
  }
};

Blockly.Blocks['arduino_delay_microseconds'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Wait')
        .appendField(new Blockly.FieldNumber(100, 0), 'US')
        .appendField('microseconds  (1 000 000 µs = 1 second)');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(42);
    this.setTooltip('Extremely short pause — useful for precise timing (e.g. ultrasonic sensor pulses).');
  }
};

// Expression block — milliseconds since board started
Blockly.Blocks['arduino_millis'] = {
  init: function () {
    this.appendDummyInput().appendField('⏱ Time since start (in ms)');
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('How many milliseconds have passed since the Arduino was turned on. Useful for non-blocking timers.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// VARIABLES
// ════════════════════════════════════════════════════════════════════════════

// Fixed-value declaration: int name = 0;
Blockly.Blocks['arduino_variable_int'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Create number called')
        .appendField(new Blockly.FieldTextInput('myNumber'), 'NAME')
        .appendField('= ')
        .appendField(new Blockly.FieldNumber(0), 'VALUE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(222);
    this.setTooltip('Creates a whole number (integer) variable and gives it a starting value.');
  }
};

// Expression-socket declaration: int name = [any block]
Blockly.Blocks['arduino_variable_int_expr'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Create number called')
        .appendField(new Blockly.FieldTextInput('myNumber'), 'NAME')
        .appendField('=');
    this.appendValueInput('VALUE')
        .setCheck('Number');
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(222);
    this.setTooltip('Create a number variable and set it to the result of a sensor reading, math, etc.');
  }
};

// Reassignment: name = [any block]
Blockly.Blocks['arduino_variable_assign'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Set variable')
        .appendField(new Blockly.FieldTextInput('myNumber'), 'NAME')
        .appendField('to');
    this.appendValueInput('VALUE')
        .setCheck(null);
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(222);
    this.setTooltip('Update an existing variable with a new value or sensor reading.');
  }
};

// Fixed-value bool declaration
Blockly.Blocks['arduino_variable_bool'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Create yes/no variable called')
        .appendField(new Blockly.FieldTextInput('myFlag'), 'NAME')
        .appendField('=')
        .appendField(new Blockly.FieldDropdown([
          ['No  (false)', 'false'], ['Yes (true)', 'true'],
        ]), 'VALUE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(222);
    this.setTooltip('A variable that can only be "yes" (true) or "no" (false). Good for on/off flags.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// SERIAL
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_serial_begin'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Start Serial Monitor at')
        .appendField(new Blockly.FieldDropdown([
          ['9600 baud', '9600'], ['115200 baud', '115200'],
          ['57600 baud', '57600'], ['38400 baud', '38400'],
        ]), 'BAUD')
        .appendField('speed');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Turns on the Serial Monitor so you can see messages from your Arduino. Add this to "Run once at start". Use 9600 if unsure.');
  }
};

Blockly.Blocks['arduino_serial_print'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Show text')
        .appendField(new Blockly.FieldTextInput('Hello'), 'VALUE')
        .appendField('on Serial Monitor');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Prints text to the Serial Monitor. The next print continues on the same line.');
  }
};

Blockly.Blocks['arduino_serial_println'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Show text')
        .appendField(new Blockly.FieldTextInput('Hello'), 'VALUE')
        .appendField('on Serial Monitor  + new line');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Prints text then moves to a new line, like pressing Enter.');
  }
};

// Serial.print with expression socket
Blockly.Blocks['arduino_serial_print_expr'] = {
  init: function () {
    this.appendDummyInput().appendField('Show');
    this.appendValueInput('VALUE').setCheck(null);
    this.appendDummyInput().appendField('on Serial Monitor');
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Shows a sensor value, variable, or calculation result in the Serial Monitor.');
  }
};

Blockly.Blocks['arduino_serial_println_expr'] = {
  init: function () {
    this.appendDummyInput().appendField('Show');
    this.appendValueInput('VALUE').setCheck(null);
    this.appendDummyInput().appendField('on Serial Monitor  + new line');
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Shows a value in the Serial Monitor and then starts a new line.');
  }
};

// Serial.available() — expression
Blockly.Blocks['arduino_serial_available'] = {
  init: function () {
    this.appendDummyInput().appendField('Bytes waiting in Serial inbox');
    this.setOutput(true, 'Number');
    this.setColour(185);
    this.setTooltip('Returns how many bytes are waiting to be read from the computer. Use in an "if" block to check before reading.');
  }
};

// Serial.read() — expression
Blockly.Blocks['arduino_serial_read'] = {
  init: function () {
    this.appendDummyInput().appendField('Read next byte from Serial');
    this.setOutput(true, 'Number');
    this.setColour(185);
    this.setTooltip('Read a single byte sent from your computer. Returns -1 if nothing is available.');
  }
};

// Serial.flush() — statement
Blockly.Blocks['arduino_serial_flush'] = {
  init: function () {
    this.appendDummyInput().appendField('Wait for Serial to finish sending');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Pauses until all outgoing Serial data has been fully transmitted.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// DIGITAL I/O — EXTRA
// ════════════════════════════════════════════════════════════════════════════

Blockly.Blocks['arduino_pin_toggle'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Flip pin')
        .appendField(new Blockly.FieldNumber(13, 0, 53), 'PIN')
        .appendField('(ON → OFF  or  OFF → ON)');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Switches a pin to the opposite state. Great for blinking an LED without knowing its current state.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// ANALOG I/O — EXTRA
// ════════════════════════════════════════════════════════════════════════════

// constrain(val, min, max) — expression
Blockly.Blocks['arduino_constrain'] = {
  init: function () {
    this.appendDummyInput().appendField('Keep');
    this.appendValueInput('VAL').setCheck('Number');
    this.appendDummyInput().appendField('between min');
    this.appendValueInput('MIN').setCheck('Number');
    this.appendDummyInput().appendField('and max');
    this.appendValueInput('MAX').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
    this.setColour(185);
    this.setTooltip('Clamps a value so it never goes below the minimum or above the maximum. Useful for keeping sensor data in range.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// VARIABLES — EXTRA TYPES & COMPOUND OPERATORS
// ════════════════════════════════════════════════════════════════════════════

// float variable declaration
Blockly.Blocks['arduino_variable_float'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Create decimal number called')
        .appendField(new Blockly.FieldTextInput('myDecimal'), 'NAME')
        .appendField('=')
        .appendField(new Blockly.FieldNumber(0.0), 'VALUE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(222);
    this.setTooltip('Creates a variable that can hold decimal numbers like 3.14 or 0.75.');
  }
};

// String variable declaration
Blockly.Blocks['arduino_variable_string'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Create text variable called')
        .appendField(new Blockly.FieldTextInput('myText'), 'NAME')
        .appendField('=  "')
        .appendField(new Blockly.FieldTextInput('hello'), 'VALUE')
        .appendField('"');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(222);
    this.setTooltip('Creates a variable that holds a piece of text (a "String").');
  }
};

// Variable value reader — expression
Blockly.Blocks['arduino_variable_get'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Value of variable')
        .appendField(new Blockly.FieldTextInput('myNumber'), 'NAME');
    this.setOutput(true, null);
    this.setColour(222);
    this.setTooltip('Reads the current value of a variable. Plug this into math, logic, or other blocks.');
  }
};

// Compound assignment: +=, -=, *=, /=, reset to 0
Blockly.Blocks['arduino_variable_compound'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Change')
        .appendField(new Blockly.FieldTextInput('myNumber'), 'NAME')
        .appendField(new Blockly.FieldDropdown([
          ['by adding',        '+='],
          ['by subtracting',   '-='],
          ['by multiplying by','*='],
          ['by dividing by',   '/='],
          ['reset to 0',       '= 0'],
        ]), 'OP')
        .appendField(new Blockly.FieldNumber(1), 'VALUE');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(222);
    this.setTooltip('Modify a variable: add to it, subtract, multiply, divide, or reset to zero.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// MATH — EXTRA FUNCTIONS
// ════════════════════════════════════════════════════════════════════════════

// modulo: a % b
Blockly.Blocks['arduino_math_modulo'] = {
  init: function () {
    this.appendValueInput('A').setCheck('Number');
    this.appendDummyInput().appendField('remainder ÷');
    this.appendValueInput('B').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('The remainder after dividing A by B. e.g. 7 remainder ÷ 3 = 1. Useful for "every Nth time" patterns.');
  }
};

// abs(x)
Blockly.Blocks['arduino_math_abs'] = {
  init: function () {
    this.appendDummyInput().appendField('Absolute value of');
    this.appendValueInput('VALUE').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('Always returns a positive number — removes the minus sign. e.g. absolute value of -5 = 5.');
  }
};

// sqrt(x)
Blockly.Blocks['arduino_math_sqrt'] = {
  init: function () {
    this.appendDummyInput().appendField('Square root of');
    this.appendValueInput('VALUE').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('Returns the square root of a number. e.g. √9 = 3.');
  }
};

// pow(x, y)
Blockly.Blocks['arduino_math_pow'] = {
  init: function () {
    this.appendValueInput('BASE').setCheck('Number');
    this.appendDummyInput().appendField('to the power of');
    this.appendValueInput('EXP').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('Raises a number to a power. e.g. 2 to the power of 3 = 8.');
  }
};

// random(min, max)
Blockly.Blocks['arduino_math_random'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Random number from')
        .appendField(new Blockly.FieldNumber(0), 'MIN')
        .appendField('to')
        .appendField(new Blockly.FieldNumber(100), 'MAX');
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('Picks a random whole number between the two limits (min is included, max is excluded).');
  }
};

// round(x)
Blockly.Blocks['arduino_math_round'] = {
  init: function () {
    this.appendDummyInput().appendField('Round');
    this.appendValueInput('VALUE').setCheck('Number');
    this.appendDummyInput().appendField('to nearest whole number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('Rounds a decimal number to the nearest whole number. e.g. 3.7 → 4, 3.2 → 3.');
  }
};

// min(a, b)
Blockly.Blocks['arduino_math_min'] = {
  init: function () {
    this.appendDummyInput().appendField('Smaller of');
    this.appendValueInput('A').setCheck('Number');
    this.appendDummyInput().appendField('and');
    this.appendValueInput('B').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('Returns whichever of the two numbers is smaller.');
  }
};

// max(a, b)
Blockly.Blocks['arduino_math_max'] = {
  init: function () {
    this.appendDummyInput().appendField('Larger of');
    this.appendValueInput('A').setCheck('Number');
    this.appendDummyInput().appendField('and');
    this.appendValueInput('B').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('Returns whichever of the two numbers is larger.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// LOOPS — EXTRA
// ════════════════════════════════════════════════════════════════════════════

// break
Blockly.Blocks['arduino_break'] = {
  init: function () {
    this.appendDummyInput().appendField('🛑  Stop loop now');
    this.setPreviousStatement(true, null);
    this.setColour(140);
    this.setTooltip('Immediately exits the current loop. Nothing after this in the loop will run.');
  }
};

// continue
Blockly.Blocks['arduino_continue'] = {
  init: function () {
    this.appendDummyInput().appendField('⏭  Skip to next repeat');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(140);
    this.setTooltip('Skips the rest of this loop pass and starts the next one immediately.');
  }
};

// do...while
Blockly.Blocks['arduino_do_while'] = {
  init: function () {
    this.appendDummyInput().appendField('Do this at least once');
    this.appendStatementInput('DO').setCheck(null);
    this.appendDummyInput().appendField('then keep repeating while');
    this.appendValueInput('CONDITION').setCheck('Boolean');
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(140);
    this.setTooltip('Runs the blocks inside at least once, then keeps repeating as long as the condition is true.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// TIME — EXTRA
// ════════════════════════════════════════════════════════════════════════════

// micros() — expression
Blockly.Blocks['arduino_micros'] = {
  init: function () {
    this.appendDummyInput().appendField('⏱ Time since start (in µs)');
    this.setOutput(true, 'Number');
    this.setColour(42);
    this.setTooltip('Like "Time since start (ms)" but in microseconds — 1000× more precise. Overflows after ~70 minutes.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// LED HELPERS
// ════════════════════════════════════════════════════════════════════════════

// Blink LED N times with delay
Blockly.Blocks['arduino_led_blink'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Blink LED on pin')
        .appendField(new Blockly.FieldNumber(13, 0, 53), 'PIN')
        .appendField(' ')
        .appendField(new Blockly.FieldNumber(3, 1), 'TIMES')
        .appendField('times,  pause')
        .appendField(new Blockly.FieldNumber(500, 1), 'MS')
        .appendField('ms between each');
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(185);
    this.setTooltip('Blinks an LED a set number of times. The pause controls how fast it blinks.');
  }
};

// ════════════════════════════════════════════════════════════════════════════
// BUTTON & INPUT HELPERS
// ════════════════════════════════════════════════════════════════════════════

// Active-low button read (INPUT_PULLUP wiring — LOW means pressed)
Blockly.Blocks['arduino_button_pressed'] = {
  init: function () {
    this.appendDummyInput()
        .appendField('Button on pin')
        .appendField(new Blockly.FieldNumber(2, 0, 53), 'PIN')
        .appendField('is being pressed');
    this.setOutput(true, 'Boolean');
    this.setColour(185);
    this.setTooltip('Returns YES if the button is currently pressed. Wire button between pin and GND, and set pin to "Input with Pull-up".');
  }
};
