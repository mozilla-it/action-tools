.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: clean
clean: ## Remove dependencies, tool caches, and build artifacts
	@rm -rf .pytest_cache .ruff_cache dist .venv .mypy_cache .tox

.PHONY: format
format: pyproject.toml ## Run code formatting tools (update in place)
	@uv run ruff format . && uv run ruff check --fix .

.PHONY: init
init: pyproject.toml ## Set up virtual environment and install dependencies
	@uv sync --locked --all-extras --dev

.PHONY: lint
lint: pyproject.toml ## Run linting tools and check formatting
	@uv run ruff check . && uv run ruff format --check

.PHONY: test
test: pyproject.toml ## Run tests
	@uv run tox

