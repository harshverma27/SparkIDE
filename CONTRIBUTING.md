# Contributing to SparkIDE

Thanks for your interest in improving SparkIDE! This document covers how to set up a development environment, the conventions used in this codebase, and how to submit changes.

## Getting Started

1. Fork the repository and clone your fork:
   ```bash
   git clone https://github.com/<your-username>/SparkIDE.git
   cd SparkIDE
   ```
2. Run the full setup (creates `.venv`, installs Python deps, installs `arduino-cli` + the AVR core):
   ```bash
   make setup
   ```
3. Launch the app to confirm everything works:
   ```bash
   make run
   ```

## Development Workflow

- Create a feature branch off `main`:
  ```bash
  git checkout -b feat/my-change
  ```
- Make your changes. Keep commits focused — one logical change per commit.
- Run the test suite before opening a PR:
  ```bash
  make test
  ```
- Push your branch and open a pull request against `main`.

## Coding Conventions

- **Python**: Follow PEP 8. Use type hints for new functions where practical. Keep UI styling consistent with the existing design tokens defined at the top of `ui/main_window.py`, `ui/code_panel.py`, and `ui/log_panel.py` (the "Hybrid Lab Console" palette).
- **Blockly (JS)**: New blocks belong in `blockly/blocks/arduino_blocks.js`, and their C++ output belongs in `blockly/generators/arduino_generator.js`. Assign new categories a `colour` from the existing 4-family palette (green/teal/amber/blue-gray) rather than introducing new hues.
- **Commit messages**: Use a short conventional prefix — `feat:`, `fix:`, `docs:`, `ui:`, `refactor:`, `test:` — followed by an imperative summary, e.g. `feat: add servo motor block`.

## Adding a New Block

1. Define the block shape and field layout in `blockly/blocks/arduino_blocks.js`.
2. Add the corresponding C++ code generator in `blockly/generators/arduino_generator.js`.
3. Register the block in the relevant category of the `TOOLBOX` definition in `blockly/index.html`.
4. If it's a new category, pick a `colour` consistent with the existing category families.

## Reporting Bugs / Requesting Features

Open an issue on GitHub with:

- A clear description of the problem or proposal.
- Steps to reproduce (for bugs), including your Linux distro and Python version.
- Screenshots or recordings for UI issues — these are especially helpful.

## Pull Request Checklist

- [ ] `make test` passes.
- [ ] The app launches and the relevant feature works (`make run`).
- [ ] New blocks have both a block definition and a generator.
- [ ] UI changes follow the existing visual design tokens.
- [ ] README/CHANGELOG updated if behavior or setup steps changed.

## Code of Conduct

Be respectful and constructive. Disagreements about code are fine; personal attacks are not. Maintainers may close issues or PRs that don't follow these guidelines.
