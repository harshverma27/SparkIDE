# User-Defined Functions (Advanced Blocks) — Design

Date: 2026-06-13
Status: Approved for implementation

## Goal

Implement the roadmap item "Advanced Blocks: User-defined functions (multi-pass C++
generation)". Users can define named functions (with optional `int` parameters and an
optional `int` return value) as blocks, call them from `setup()`/`loop()` or other
functions, and see correct C++ emitted with the function definitions placed above
`setup()`/`loop()`.

## Approach

Use Blockly's **built-in procedure blocks** rather than custom blocks:

- `procedures_defnoreturn` → `void name(int a, ...) { ... }`
- `procedures_defreturn`   → `int name(int a, ...) { ...; return expr; }`
- `procedures_callnoreturn` / `procedures_callreturn` → `name(args);` / `name(args)`
- `procedures_ifreturn`    → `if (cond) { return [expr]; }`

Rationale: these blocks ship in the already-vendored `blocks_compressed.js` (offline
constraint holds), provide the Scratch-like "My Blocks" UX including the parameter
mutator dialog and automatic call-block synchronisation, and only need C++ generators.
Alternatives considered: (a) custom no-parameter def/call blocks — too weak, no
parameters; (b) custom blocks with bespoke typed-parameter mutators — large UI effort
for marginal benefit over `int`-typed parameters. All parameters and return values are
`int`, consistent with the existing block set (digitalRead, analogRead, map, etc. are
all integer-valued). Typed parameters can be layered on later.

## Components

### `blockly/index.html`
- Add toolbox category `{ kind: "category", name: "Functions", colour: "222",
  custom: "PROCEDURE" }` — Blockly populates it dynamically with definition blocks and
  one call block per defined function.
- Add `procedure_blocks: { colourPrimary: "222" }` to `WORKSPACE_THEME.blockStyles`.

### `blockly/blocks/arduino_blocks.js`
- Override the relevant `Blockly.Msg` strings (after `vendor/en.js` loads) with
  beginner-friendly labels for the procedure blocks, matching the plain-English house
  style.

### `blockly/generators/arduino_generator.js`
- **`init(workspace)` override**: reset `definitions_`, create/reset `nameDB_`
  (`Blockly.Names` seeded with C++/Arduino reserved words such as `setup`, `loop`,
  `int`, `delay`...), populate variable and procedure names.
- **`finish(code)` override (the "multi-pass" step)**: prepend collected function
  prototypes (forward declarations) and then full definitions above the
  `setup()`/`loop()` code, separated by blank lines.
- **`scrub_` override**: concatenate code from next-statement blocks. This also fixes a
  pre-existing bug where only the first block of any statement chain was generated
  (Blockly 10's default `scrub_` does not follow next connections).
- **`forBlock` generators** for the five procedure block types above. Def-block
  generators return `null` and stash their code in `definitions_` so top-level def
  blocks don't leak into the setup/loop output stream.

### Tests
- `tests/generate_code.js` — headless Node harness: reads workspace-serialization JSON
  on stdin, loads vendored Blockly + blocks + generator, prints generated C++.
- `tests/test_function_blocks.py` — drives the harness via subprocess (skips if `node`
  absent). Asserts: void function def+call; function with params and return used as an
  expression; definitions and prototypes placed above `setup()`; statement-chain
  regression (scrub_ fix); existing block output unchanged.
- Existing static tests in `test_blockly_foundation.py` continue to pass (the new
  toolbox category adds no explicit block types).

## Error handling
- A call block whose definition was deleted: Blockly disables orphaned call blocks
  automatically; disabled blocks generate no code.
- Name collisions with C++ keywords/Arduino identifiers are avoided via the
  `nameDB_` reserved-word list.

## Docs
- README roadmap: split the combined "Advanced Blocks" item and check off
  user-defined functions. CHANGELOG: add an Unreleased entry.
