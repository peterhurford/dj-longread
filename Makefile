.DEFAULT_GOAL := help

.PHONY: run
run: ## Run Django
	poetry run python manage.py runserver

.PHONY: migrate
migrate: ## Run Django migrations
	poetry run python manage.py makemigrations && python manage.py makemigrations link && poetry run python manage.py migrate

.PHONY: setup ## Install Python deps
setup: poetry-setup
	pip install poetry
	poetry install

.PHONY: build
build: ## Build package
	poetry build

.PHONY: update
update: ## Update the DB with the latest articles pulled from RSS
	python3 -m ingest.aggregate_feeds

.PHONY: exportdb
exportdb: ## Export the links database to CSV
	psql stanza_dev dbuser -c "\copy (SELECT * FROM link_link) TO data/export.csv WITH CSV;"

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
