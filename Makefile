.DEFAULT_GOAL := help
.PHONY: help install run worker lint format test-unit test-integration test evals

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-17s %s\n", $$1, $$2}'

install: ## Install dependencies and git hooks
	uv sync
	uv run pre-commit install

run: ## Start the internal API with auto-reload on http://localhost:8001
	uv run uvicorn editalmind_ai.main:create_app --factory --reload --port 8001

worker: ## Start a Celery worker
	uv run celery -A editalmind_ai.worker worker --loglevel INFO

lint: ## Check lint, formatting and types
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src tests

format: ## Fix lint issues and format the code
	uv run ruff check --fix .
	uv run ruff format .

test-unit: ## Run unit tests
	uv run pytest tests/unit

test-integration: ## Run integration tests (starts containers)
	uv run pytest tests/integration

test: ## Run unit and integration tests with coverage
	uv run pytest tests --cov --cov-report=term-missing --cov-report=xml

evals: ## Run evaluations against a real LLM (costs tokens)
	uv run pytest evals -m eval
