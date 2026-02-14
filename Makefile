.PHONY: help dev test lint format docker-up docker-down migrate migration backend frontend install clean

# ============================================================
# Stellapply — Development Commands
# ============================================================

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---- Setup ----

install: ## Install all dependencies (backend + frontend)
	pip install -e ".[dev]"
	cd frontend && npm ci
	playwright install chromium --with-deps
	pre-commit install
	pre-commit install --hook-type commit-msg

# ---- Infrastructure ----

docker-up: ## Start infrastructure services (postgres, redis, keycloak, minio)
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	@echo "Services started:"
	@docker compose ps

docker-down: ## Stop infrastructure services
	docker compose down

docker-clean: ## Stop services and remove volumes
	docker compose down -v

# ---- Backend ----

backend: ## Start FastAPI backend (dev mode)
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# ---- Frontend ----

frontend: ## Start Next.js frontend (dev mode)
	cd frontend && npm run dev

# ---- Dev (all together) ----

dev: docker-up ## Start everything: docker + backend + frontend
	@echo "Starting backend and frontend..."
	@$(MAKE) backend &
	@$(MAKE) frontend &
	@wait

# ---- Database ----

migrate: ## Run pending Alembic migrations
	alembic upgrade head

migration: ## Create new Alembic migration (usage: make migration msg="add users table")
	alembic revision --autogenerate -m "$(msg)"

# ---- Testing ----

test: ## Run all backend tests
	pytest -x -v

test-cov: ## Run tests with coverage report
	pytest --cov=src --cov-report=html --cov-report=term-missing

# ---- Linting ----

lint: ## Run all linters
	ruff check .
	cd frontend && npm run lint

format: ## Auto-format all code
	ruff check --fix .
	ruff format .

# ---- Cleanup ----

clean: ## Remove build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
