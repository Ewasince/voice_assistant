PYTHON_VERSION := python3.12
DEPLOY_DIR := .deploy
CHECKED_FILES := $(shell git ls-files "*.py")
PYTEST_ARGS := --cov
PYTEST_REPORT_ARGS :=  --cov-report=xml:coverage.xml

.PHONY: install
install:
	@poetry env use $(PYTHON_VERSION)
	@poetry install
	@poetry run pre-commit install

.PHONY: lint.mypy
lint.mypy:
	@poetry run mypy

.PHONY: lint.ruff
lint.ruff:
	@poetry run ruff check . --fix

.PHONY: test.pytest
test.pytest:
	@poetry run pytest $(PYTEST_ARGS) -- tests

.PHONY: test.coverage
test.coverage:
	@poetry run pytest $(PYTEST_ARGS) $(PYTEST_REPORT_ARGS) -- tests

.PHONY: pre-commit-all
pre-commit-all:
	@poetry run pre-commit run --all-files

.PHONY: align_code
align_code:
	poetry run ruff format .
