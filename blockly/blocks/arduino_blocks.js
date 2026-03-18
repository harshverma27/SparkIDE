/**
 * blockly/blocks/arduino_blocks.js
 * Custom Blockly block DEFINITIONS for Arduino.
 *
 * What to do here:
 *   Define the visual shape, inputs, and fields of every custom Arduino block
 *   using Blockly.Blocks['block_type'] = { init: function() { ... } }
 *
 * Blocks to define (10 core blocks for v0.1):
 *
 *  1. arduino_setup_loop
 *     - A top-level container with two statement inputs: SETUP and LOOP.
 *     - Should be the "hat" block (no previous connection — it's the root).
 *     - Maps to:  void setup() { ... }  void loop() { ... }
 *
 *  2. arduino_pinmode
 *     - Fields: PIN (dropdown 0-13), MODE (dropdown INPUT/OUTPUT/INPUT_PULLUP).
 *     - Maps to:  pinMode(pin, mode);
 *
 *  3. arduino_digitalwrite
 *     - Fields: PIN (dropdown 0-13), VALUE (dropdown HIGH/LOW).
 *     - Maps to:  digitalWrite(pin, value);
 *
 *  4. arduino_digitalread
 *     - Output block (returns a value — use as an expression).
 *     - Field: PIN (dropdown 0-13).
 *     - Maps to:  digitalRead(pin)
 *
 *  5. arduino_delay
 *     - Field: MS (number input, default 1000).
 *     - Maps to:  delay(ms);
 *
 *  6. arduino_variable_int
 *     - Fields: NAME (text input), VALUE (number input).
 *     - Maps to:  int name = value;
 *     - Tip: Consider reusing Blockly's built-in Variables category instead.
 *
 *  7. arduino_variable_bool
 *     - Fields: NAME (text input), VALUE (dropdown true/false).
 *     - Maps to:  bool name = value;
 *
 *  8. arduino_serial_begin
 *     - Field: BAUD (dropdown: 9600, 115200, etc.).
 *     - Maps to:  Serial.begin(baud);
 *
 *  9. arduino_serial_print
 *     - Input: VALUE (accepts any block as expression — use value input).
 *     - Maps to:  Serial.print(value);
 *
 * 10. arduino_serial_println   (optional, easy to add alongside #9)
 *     - Same as above but Maps to:  Serial.println(value);
 *
 * Styling tips:
 *   - Use this.setColour(hue) to colour-code categories:
 *       Structure blocks:  hue 120 (green)
 *       Digital I/O:       hue 210 (blue)
 *       Time:              hue 30  (orange)
 *       Serial:            hue 270 (purple)
 *   - Use this.setTooltip() for hover tooltips.
 *   - Use this.setHelpUrl('https://www.arduino.cc/reference/en/') for help links.
 */

// TODO: define Blockly.Blocks['arduino_setup_loop'] = { init: function() { ... } };
// TODO: define Blockly.Blocks['arduino_pinmode']    = { init: function() { ... } };
// TODO: define Blockly.Blocks['arduino_digitalwrite'] = { ... };
// TODO: define Blockly.Blocks['arduino_digitalread']  = { ... };
// TODO: define Blockly.Blocks['arduino_delay']         = { ... };
// TODO: define Blockly.Blocks['arduino_variable_int']  = { ... };
// TODO: define Blockly.Blocks['arduino_variable_bool'] = { ... };
// TODO: define Blockly.Blocks['arduino_serial_begin']  = { ... };
// TODO: define Blockly.Blocks['arduino_serial_print']  = { ... };
