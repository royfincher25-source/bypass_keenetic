# =============================================================================
# MAKEFILE ДЛЯ BYPASS_KEENETIC
# =============================================================================
# Автоматизация задач разработки, тестирования и развёртывания
# =============================================================================

.PHONY: help install install-dev install-test lint format test test-cov clean validate setup-venv

# -----------------------------------------------------------------------------
# VARIABLES
# -----------------------------------------------------------------------------
PYTHON := python3
PIP := pip3
PROJECT_DIR := $(shell pwd)
BOT3_DIR := $(PROJECT_DIR)/bot3
BOTLIGHT_DIR := $(PROJECT_DIR)/botlight

# -----------------------------------------------------------------------------
# HELP
# -----------------------------------------------------------------------------
help:
	@echo "Bypass Keenetic - Makefile Commands"
	@echo "===================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup-venv     - Создать виртуальное окружение"
	@echo "  make install        - Установить основные зависимости"
	@echo "  make install-dev    - Установить зависимости для разработки"
	@echo "  make install-test   - Установить зависимости для тестирования"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           - Запустить линтеры (flake8, black, isort)"
	@echo "  make format         - Форматировать код (black, isort)"
	@echo "  make validate       - Валидировать конфигурационные файлы"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Запустить тесты"
	@echo "  make test-cov       - Запустить тесты с покрытием"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Очистить временные файлы и кеш"
	@echo ""

# -----------------------------------------------------------------------------
# SETUP
# -----------------------------------------------------------------------------
setup-venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "✓ Virtual environment created"
	@echo ""
	@echo "Activate with:"
	@echo "  source venv/bin/activate  (Linux/Mac)"
	@echo "  venv\Scripts\activate     (Windows)"

install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Dependencies installed"

install-dev:
	@echo "Installing development dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@echo "✓ Development dependencies installed"

install-test:
	@echo "Installing test dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-test.txt
	@echo "✓ Test dependencies installed"

# -----------------------------------------------------------------------------
# CODE QUALITY
# -----------------------------------------------------------------------------
lint: lint-flake8 lint-black lint-isort
	@echo "✓ All lint checks passed"

lint-flake8:
	@echo "Running flake8..."
	flake8 $(BOT3_DIR) $(BOTLIGHT_DIR) \
		--count \
		--select=E9,F63,F7,F82 \
		--show-source \
		--statistics \
		--exclude=.git,__pycache__,venv,.venv,*.pyc

lint-black:
	@echo "Running black check..."
	black --check $(BOT3_DIR) $(BOTLIGHT_DIR) \
		--exclude='.git|__pycache__|venv|.venv|*.pyc'

lint-isort:
	@echo "Running isort check..."
	isort --check-only $(BOT3_DIR) $(BOTLIGHT_DIR) \
		--skip=.git --skip=venv --skip=.venv --skip=__pycache__

format: format-black format-isort
	@echo "✓ Code formatted"

format-black:
	@echo "Formatting with black..."
	black $(BOT3_DIR) $(BOTLIGHT_DIR) \
		--exclude='.git|__pycache__|venv|.venv|*.pyc'

format-isort:
	@echo "Sorting imports with isort..."
	isort $(BOT3_DIR) $(BOTLIGHT_DIR) \
		--skip=.git --skip=venv --skip=.venv --skip=__pycache__

validate: validate-env validate-python
	@echo "✓ All validations passed"

validate-env:
	@echo "Validating .env.example..."
	@test -f .env.example || (echo "❌ .env.example not found" && exit 1)
	@grep -q "TELEGRAM_BOT_TOKEN=" .env.example || (echo "❌ TELEGRAM_BOT_TOKEN not in .env.example" && exit 1)
	@grep -q "TELEGRAM_USERNAMES=" .env.example || (echo "❌ TELEGRAM_USERNAMES not in .env.example" && exit 1)
	@echo "✓ .env.example is valid"

validate-python:
	@echo "Validating Python syntax..."
	$(PYTHON) -m py_compile $(BOT3_DIR)/bot_config.py
	$(PYTHON) -m py_compile $(BOTLIGHT_DIR)/bot_config.py
	@echo "✓ Python files are valid"

# -----------------------------------------------------------------------------
# TESTING
# -----------------------------------------------------------------------------
test:
	@echo "Running tests..."
	@if [ -d "tests" ]; then \
		pytest tests/ -v; \
	else \
		echo "⚠️  tests/ directory not found. Create tests to run."; \
	fi

test-cov:
	@echo "Running tests with coverage..."
	@if [ -d "tests" ]; then \
		pytest tests/ -v --cov=$(BOT3_DIR) --cov=$(BOTLIGHT_DIR) --cov-report=html; \
		echo "Coverage report: htmlcov/index.html"; \
	else \
		echo "⚠️  tests/ directory not found. Create tests to run."; \
	fi

# -----------------------------------------------------------------------------
# CLEANUP
# -----------------------------------------------------------------------------
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .venv venv ENV/
	@echo "✓ Cleanup complete"

# -----------------------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------------------
security-check:
	@echo "Running security check..."
	pip-audit --requirement requirements.txt

# -----------------------------------------------------------------------------
# PRE-COMMIT
# -----------------------------------------------------------------------------
pre-commit-install:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "✓ Pre-commit hooks installed"

pre-commit-run:
	@echo "Running pre-commit checks..."
	pre-commit run --all-files
