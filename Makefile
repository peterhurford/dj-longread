.DEFAULT_GOAL := help

.PHONY: run
run: ## Run Django
	poetry run python manage.py runserver

.PHONY: migrate
migrate: ## Run Django migrations
	poetry run python manage.py makemigrations && python manage.py makemigrations link && poetry run python manage.py migrate

.PHONY: setup
setup: ## Install Python deps
	pip install poetry
	poetry update
	poetry install

.PHONY: build
build: ## Build package
	poetry build

.PHONY: update
update: ## Update the DB with the latest articles pulled from RSS
	python3 -m ingest.aggregate_feeds

.PHONY: exportdb
exportdb: ## Export the links database to CSV and upload to S3
	python3 -m ingest.export_db
	python3 -m ingest.sync_db up

.PHONY: importdb
importdb: ## Get links database from S3
	python3 -m ingest.sync_db down

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
