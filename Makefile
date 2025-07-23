.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.venv/bin/python:
	@uv venv .venv

.venv/.install.stamp: .venv/bin/python pyproject.toml
	@uv sync
	@touch .venv/.install.stamp

.PHONY: clean
clean: ## Remove dependencies, tool caches, and build artifacts
	@rm -rf .pytest_cache .ruff_cache dist .venv

.PHONY: format
format: .venv/.install.stamp ## Run code formatting tools (update in place)
	@.venv/bin/ruff format . && .venv/bin/ruff check --fix .


.PHONY: init
init: .venv/.install.stamp ## Set up virtual environment and install dependencies

.PHONY: lint
lint: .venv/.install.stamp ## Run code linting tools
	@.venv/bin/ruff check . && .venv/bin/ruff format --check

.PHONY: test
test: .venv/.install.stamp ## Run server tests
	@.venv/bin/pytest .

