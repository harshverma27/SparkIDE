<!--
Thanks for contributing to SparkIDE! Please keep the PR focused on one logical
change. Fill in the summary and tick the checklist below.
-->

## Summary

<!-- What does this PR do, and why? Link any related issue (e.g. "Closes #12"). -->

## Checklist

- [ ] `make lint` passes (ruff + ESLint).
- [ ] `make test` passes (Python) and `make test-js` passes (Blockly generators).
- [ ] The app launches and the relevant feature works (`make run`).
- [ ] New blocks have **both** a block definition (`blockly/blocks/arduino_blocks.js`)
      and a generator (`blockly/generators/arduino_generator.js`), and are
      registered in the `TOOLBOX`.
- [ ] UI changes follow the existing "Hybrid Lab Console" design tokens.
- [ ] README / CHANGELOG updated if behavior or setup steps changed.
