.PHONY: help install db-up db-ps db-down api swagger health users

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-12s %s\n", $$1, $$2}'

install: ## Install Python dependencies
	uv pip install -r requirements.txt

db-up: ## Start local PostgreSQL
	docker compose up -d

db-ps: ## Show PostgreSQL container status
	docker compose ps

db-down: ## Stop local PostgreSQL
	docker compose down

api: ## Start FastAPI server with reload
	uv run uvicorn src.api_server:app --reload

swagger: ## Print Swagger and OpenAPI URLs
	@echo "Swagger UI:  http://127.0.0.1:8000/docs"
	@echo "OpenAPI JSON: http://127.0.0.1:8000/openapi.json"

health: ## Check API health endpoint
	curl -sS http://127.0.0.1:8000/health

users: ## Query users endpoint (matches current route naming)
	curl -sS http://127.0.0.1:8000/users/get_users