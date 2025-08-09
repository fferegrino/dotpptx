SHELL := /bin/bash

# Convenience variables
UVX := uvx
BUMP := $(UVX) bump-my-version

.PHONY: help show-bump version check-clean bump-patch bump-minor bump-major

help: ## Show available targets
	@echo "Available targets:"
	@echo "  show-bump        - Show current version and possible bumps"
	@echo "  version          - Print current version only"
	@echo "  bump-patch       - Bump patch version (commit + tag)"
	@echo "  bump-minor       - Bump minor version (commit + tag)"
	@echo "  bump-major       - Bump major version (commit + tag)"

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


