.PHONY: help build up down logs clean test setup

help: ## Show this help message
	@echo "TherapyBot Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - copy .env.example to .env
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please update .env with your actual values"; \
	else \
		echo ".env file already exists"; \
	fi

build: ## Build all Docker images
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Show logs from all services
	docker compose logs -f

logs-backend: ## Show backend logs only
	docker compose logs -f backend

logs-frontend: ## Show frontend logs only
	docker compose logs -f frontend

clean: ## Remove all containers, volumes, and images
	docker compose down -v --rmi all

test: ## Run backend tests
	docker compose exec backend python -m pytest

health: ## Check health of all services
	@echo "Checking service health..."
	@docker compose ps
	@echo ""
	@echo "Backend health:"
	@curl -f http://localhost:8000/health || echo "Backend not healthy"
	@echo ""
	@echo "Frontend health:"
	@curl -f http://localhost:3000 || echo "Frontend not healthy"

restart: down up ## Restart all services

rebuild: down build up ## Rebuild and restart all services