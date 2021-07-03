.DEFAULT_GOAL := help

.PHONY: run
run: ## Run Django
	poetry run python manage.py runserver

.PHONY: pipeline
pipeline: ## Run the full pipeline on Heroku
	heroku run make update &&  make launch && make importdb && git add . && git commit -m "Update DB" && git push origin master && printf "%s\n" "$(date)"

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

.PHONY: local_exportdb
local_exportdb: ## Export the local links database to local CSV
	python3 -m ingest.export_db

.PHONY: exportdb
exportdb: ## Export the links database to CSV and upload to S3
	python3 -m ingest.export_db
	python3 -m ingest.sync_db --mode up

.PHONY: importdb
importdb: ## Get links database from S3
	python3 -m ingest.sync_db --mode down

.PHONY: launch
launch: ## Open the website
	open https://guarded-everglades-89687.herokuapp.com/

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
