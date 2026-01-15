.PHONY: help install install-ai install-dev dev worker test lint typecheck up down reset logs psql redis-cli clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# Installation
# =============================================================================

install:  ## Install core dependencies
	pip install -e .

install-ai:  ## Install with AI support (OpenAI + Anthropic)
	pip install -e ".[ai]"

install-dev:  ## Install dev dependencies (testing, linting)
	pip install -e ".[dev]"

# =============================================================================
# Development
# =============================================================================

dev:  ## Start API server with auto-reload
	uvicorn app.main:app --reload

worker:  ## Start background worker
	python -m app.worker

test:  ## Run tests
	pytest tests/ -v

lint:  ## Run linter (ruff)
	ruff check .
	ruff format --check .

format:  ## Format code with ruff
	ruff format .
	ruff check --fix .

typecheck:  ## Run type checker (mypy)
	mypy app --ignore-missing-imports

# =============================================================================
# Docker
# =============================================================================

up:  ## Start PostgreSQL and Redis containers
	docker-compose up -d

down:  ## Stop containers
	docker-compose down

reset:  ## Stop containers and delete volumes (reset database)
	docker-compose down -v

logs:  ## Tail container logs
	docker-compose logs -f

# =============================================================================
# Database
# =============================================================================

psql:  ## Connect to PostgreSQL
	docker-compose exec postgres psql -U lifeos -d lifeos

migrate:  ## Run database migrations manually
	docker-compose exec postgres psql -U lifeos -d lifeos -f /docker-entrypoint-initdb.d/001_stage8_audit_and_lifecycle.sql
	docker-compose exec postgres psql -U lifeos -d lifeos -f /docker-entrypoint-initdb.d/002_stage9_ai_suggestions.sql

# =============================================================================
# Redis
# =============================================================================

redis-cli:  ## Connect to Redis CLI
	docker-compose exec redis redis-cli

# =============================================================================
# Cleanup
# =============================================================================

clean:  ## Remove Python cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
