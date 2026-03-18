# ==============================================================================
# SparkIDE — Makefile
# One-command setup for a brand new Linux machine.
#
# Targets:
#   make setup          → Full first-time setup (venv + pip + arduino-cli + core)
#   make run            → Activate venv and launch SparkIDE
#   make test           → Run all Python unit tests
#   make install-cli    → Install arduino-cli only
#   make install-core   → Install Arduino AVR core only (arduino:avr)
#   make clean          → Remove .venv and build artefacts
#   make help           → Show this help
# ==============================================================================

PYTHON      := python3
VENV_DIR    := .venv
VENV_PYTHON := $(VENV_DIR)/bin/python
VENV_PIP    := $(VENV_DIR)/bin/pip
CLI_INSTALL := https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh

# Detect where arduino-cli ends up after install
ARDUINO_CLI := $(shell which arduino-cli 2>/dev/null || echo "$(HOME)/bin/arduino-cli")

.PHONY: setup run test install-cli install-core clean help

# ── Default target ─────────────────────────────────────────────────────────────
all: help

# ── Full setup ─────────────────────────────────────────────────────────────────
setup: _check-python _venv _pip install-cli install-core
	@echo ""
	@echo "✅  SparkIDE setup complete!"
	@echo ""
	@echo "    To activate the virtual environment:"
	@echo "      source $(VENV_DIR)/bin/activate"
	@echo ""
	@echo "    To run SparkIDE:"
	@echo "      make run"
	@echo ""

# ── Check Python 3 is available ────────────────────────────────────────────────
_check-python:
	@echo "🔍  Checking for Python 3..."
	@$(PYTHON) --version >/dev/null 2>&1 || \
		(echo "❌  python3 not found. Install it with: sudo apt install python3 python3-pip python3-venv" && exit 1)
	@echo "✅  $(shell $(PYTHON) --version) found."

# ── Create virtual environment ─────────────────────────────────────────────────
_venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "📦  Creating virtual environment in $(VENV_DIR)/..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "✅  Virtual environment created."; \
	else \
		echo "✅  Virtual environment already exists, skipping."; \
	fi

# ── Install Python dependencies ────────────────────────────────────────────────
_pip: _venv
	@echo "📥  Installing Python dependencies from requirements.txt..."
	@$(VENV_PIP) install --upgrade pip --quiet
	@$(VENV_PIP) install -r requirements.txt
	@echo "✅  Python dependencies installed."

# ── Install arduino-cli ────────────────────────────────────────────────────────
install-cli:
	@if command -v arduino-cli >/dev/null 2>&1; then \
		echo "✅  arduino-cli already installed: $$(arduino-cli version)"; \
	else \
		echo "📥  Installing arduino-cli..."; \
		mkdir -p $(HOME)/bin; \
		curl -fsSL $(CLI_INSTALL) | BINDIR=$(HOME)/bin sh; \
		echo ""; \
		echo "⚠️   arduino-cli installed to $(HOME)/bin."; \
		echo "    Make sure $(HOME)/bin is in your PATH. Add to ~/.bashrc or ~/.zshrc:"; \
		echo "      export PATH=\"\$$HOME/bin:\$$PATH\""; \
		echo "    Then reload: source ~/.bashrc"; \
	fi

# ── Install Arduino AVR core (for Uno / Nano) ──────────────────────────────────
install-core:
	@echo "📥  Updating arduino-cli index..."
	@arduino-cli core update-index 2>/dev/null || $(HOME)/bin/arduino-cli core update-index
	@echo "📥  Installing Arduino AVR core (arduino:avr) — needed for Uno / Nano..."
	@arduino-cli core install arduino:avr 2>/dev/null || $(HOME)/bin/arduino-cli core install arduino:avr
	@echo "✅  Arduino AVR core installed."

# ── Launch SparkIDE ────────────────────────────────────────────────────────────
run: _venv
	@echo "🚀  Launching SparkIDE..."
	@$(VENV_PYTHON) main.py

# ── Run tests ─────────────────────────────────────────────────────────────────
test: _venv
	@echo "🧪  Running tests..."
	@$(VENV_PYTHON) -m pytest tests/ -v

# ── Clean ─────────────────────────────────────────────────────────────────────
clean:
	@echo "🧹  Removing virtual environment and build artefacts..."
	@rm -rf $(VENV_DIR) __pycache__ .pytest_cache build/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅  Clean complete."

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  SparkIDE — Makefile targets"
	@echo ""
	@echo "  make setup          Full first-time setup (venv + pip + arduino-cli + AVR core)"
	@echo "  make run            Launch SparkIDE"
	@echo "  make test           Run Python unit tests"
	@echo "  make install-cli    Install arduino-cli only"
	@echo "  make install-core   Install Arduino AVR core (arduino:avr)"
	@echo "  make clean          Remove .venv and all build artefacts"
	@echo "  make help           Show this help"
	@echo ""
