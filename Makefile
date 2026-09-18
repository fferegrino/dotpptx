SHELL := /bin/bash

# Convenience variables
UVX := uvx
BUMP := $(UVX) bump-my-version
RUFF := $(UVX) ruff
PYTEST := uv run pytest
MYPY := uv run mypy

.PHONY: help show-bump version check-clean bump-patch bump-minor bump-major fmt lint test coverage coverage-html coverage-report

help: ## Show available targets
	@echo "Available targets:"
	@echo "  show-bump        - Show current version and possible bumps"
	@echo "  version          - Print current version only"
	@echo "  bump-patch       - Bump patch version (commit + tag)"
	@echo "  bump-minor       - Bump minor version (commit + tag)"
	@echo "  bump-major       - Bump major version (commit + tag)"
	@echo "  fmt              - Format code"
	@echo "  lint             - Lint code"
	@echo "  unit             - Run unit tests"
	@echo "  e2e              - Run end-to-end tests"
	@echo "  test             - Run all tests"
	@echo "  coverage         - Run tests with coverage report"
	@echo "  coverage-html    - Generate HTML coverage report"
	@echo "  coverage-report  - Show detailed coverage report"

check-clean: ## Ensure git working tree is clean
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: git working tree is not clean. Commit or stash changes first."; \
		exit 1; \
	fi

show-bump: ## Show current version and possible bumps
	$(BUMP) show-bump

version: ## Print current version only
	@$(BUMP) show-bump | head -n1 | awk '{print $$1}'

bump-patch: check-clean ## Bump patch version (commit + tag)
	$(BUMP) bump patch

bump-minor: check-clean ## Bump minor version (commit + tag)
	$(BUMP) bump minor

bump-major: check-clean ## Bump major version (commit + tag)
	$(BUMP) bump major

fmt:
	$(RUFF) format
	$(RUFF) check --fix

lint:
	$(RUFF) check
	$(MYPY) src

unit:
	$(PYTEST) tests/unit

e2e:
	$(PYTEST) tests/e2e

test: unit e2e

coverage:
	$(PYTEST) --cov=dotpptx --cov-report=term-missing tests/

coverage-html:
	$(PYTEST) --cov=dotpptx --cov-report=html --cov-report=term tests/
	@echo "Coverage report generated in htmlcov/index.html"

coverage-report:
	$(PYTEST) --cov=dotpptx --cov-report=term-missing --cov-report=html tests/
	@echo ""
	@echo "Detailed coverage report:"
	@$(PYTEST) --cov=dotpptx --cov-report=term tests/ --quiet
