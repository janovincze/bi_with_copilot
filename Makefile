# Copilot Analytics - Makefile
# Common commands for development and running the application

.PHONY: setup run-flask run-streamlit copilot-auth copilot-start dbt-build dbt-docs train clean help docker-auth docker-up docker-build docker-streamlit docker-flask docker-dev docker-down docker-clean

# Default target
help:
	@echo "Copilot Analytics - Available Commands"
	@echo ""
	@echo "Docker (Recommended):"
	@echo "  make docker-auth    - Authenticate with GitHub Copilot (first time)"
	@echo "  make docker-up      - Start everything (copilot-api + streamlit)"
	@echo "  make docker-down    - Stop all services"
	@echo "  make docker-flask   - Run Flask instead of Streamlit"
	@echo "  make docker-build   - Rebuild Docker images"
	@echo "  make docker-clean   - Remove Docker images and volumes"
	@echo ""
	@echo "Local Setup:"
	@echo "  make setup          - Run full setup (venv, deps, dbt build)"
	@echo "  make copilot-auth   - Authenticate with GitHub Copilot"
	@echo "  make copilot-start  - Start the Copilot API server"
	@echo "  make run-streamlit  - Start Streamlit dashboard (port 8501)"
	@echo "  make run-flask      - Start Flask dashboard (port 8084)"
	@echo ""
	@echo "Development:"
	@echo "  make dbt-build      - Rebuild dbt models"
	@echo "  make dbt-docs       - Generate and serve dbt documentation"
	@echo "  make train          - Validate training examples"
	@echo "  make clean          - Remove generated files"
	@echo ""

# Full setup
setup:
	./setup.sh

# Copilot API commands
copilot-auth:
	npx copilot-api@latest auth

copilot-start:
	npx copilot-api@latest start --rate-limit 10 --wait

# Application commands
train:
	cd ai_dashboard && python train_vanna.py

run-flask:
	cd ai_dashboard && python app_flask.py

run-streamlit:
	cd ai_dashboard && streamlit run app_streamlit.py

# dbt commands
dbt-build:
	cd dbt_project && dbt build

dbt-seed:
	cd dbt_project && dbt seed

dbt-docs:
	cd dbt_project && dbt docs generate && dbt docs serve

dbt-test:
	cd dbt_project && dbt test

# Cleanup
clean:
	rm -rf venv
	rm -rf ai_dashboard/chroma_data
	rm -rf ai_dashboard/__pycache__
	rm -rf ai_dashboard/utils/__pycache__
	rm -f dbt_project/jaffle_shop.duckdb
	rm -f dbt_project/jaffle_shop.duckdb.wal
	rm -rf dbt_project/target
	rm -rf dbt_project/logs
	rm -rf dbt_project/dbt_packages
	rm -f .env

# Docker commands
docker-auth:
	docker compose run --rm auth

docker-up:
	docker compose up

docker-build:
	docker compose build

docker-streamlit:
	docker compose up

docker-flask:
	docker compose --profile flask up

docker-dev:
	docker compose --profile dev up

docker-down:
	docker compose down

docker-clean:
	docker compose down --rmi local --volumes
	docker volume rm copilot-analytics_copilot-credentials 2>/dev/null || true
	docker image rm copilot-analytics 2>/dev/null || true
