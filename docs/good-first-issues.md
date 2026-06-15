# Good First Issues

A backlog of small, well-scoped tasks for new contributors. Each is sized to be
completable in a single PR and touches only a couple of files. Pick one, comment
on (or open) the matching GitHub issue, and read [CONTRIBUTING.md](../CONTRIBUTING.md)
first.

> Maintainers: open these as GitHub issues labelled `good first issue` and link
> each entry below to its issue number once created.

## New blocks

Adding a block follows one pattern (see "Adding a New Block" in CONTRIBUTING):
define it in `blockly/blocks/arduino_blocks.js`, add a generator in
`blockly/generators/arduino_generator.js`, and register it in the `TOOLBOX` in
`blockly/index.html`. Add an assertion to `tests/generators.test.mjs`.

1. **`tone()` / `noTone()` blocks** — play a frequency on a pin (Digital I/O or a
   new "Sound" category). Generates `tone(pin, freq);` / `noTone(pin);`.
2. **`shiftOut()` block** — for shift registers; fields for data/clock pins, bit
   order, and value.
3. **`analogReference()` block** — dropdown for `DEFAULT`/`INTERNAL`/`EXTERNAL`.
4. **`Serial.parseInt()` / `Serial.parseFloat()` expression blocks** — extend the
   existing Serial category.
5. **Bitwise operator blocks** — `&`, `|`, `^`, `~`, `<<`, `>>` to complement the
   existing math blocks.

## Tests & quality

6. **Add a generator test for every Logic/Loops block** — extend
   `tests/generators.test.mjs` so each control-flow block has at least one
   assertion.
7. **Cover the `_parse_error` patterns** — add cases to `tests/test_arduino_cli.py`
   for each beginner-message pattern in `cli/arduino_cli.py`.

## Docs & polish

8. **Document each toolbox category in the README** — a short table of what each
   block group does, with a screenshot.
9. **Add tooltips to blocks missing them** — audit `arduino_blocks.js` for blocks
   without a `setTooltip(...)` and fill them in.
