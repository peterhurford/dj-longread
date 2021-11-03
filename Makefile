.DEFAULT_GOAL := help

.PHONY: run
run: ## Run Django
	poetry run python manage.py runserver

.PHONY: pipeline
pipeline: ## Run the full pipeline on Heroku
	heroku run make update && make launch && heroku run make exportdb && make importdb && git add data/export.csv && git commit -m "Update DB" && git push origin master; echo "$$(date)"

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

.PHONY: db_to_csv
db_to_csv: ## Export the links database to local CSV
	python3 -m ingest.export_db

.PHONY: db_from_csv
db_from_csv: ## Import the links database from local CSV
	python3 -m ingest.import_db

.PHONY: csv_to_s3
csv_to_s3: ## Upload the links CSV  file to S3
	python3 -m ingest.sync_db --mode up

.PHONY: csv_from_s3
csv_from_s3: ## Download the links CSV file from S3
	python3 -m ingest.sync_db --mode down

.PHONY: exportdb
exportdb: ## Export the links database to CSV and then to S3
	python3 -m ingest.export_db
	python3 -m ingest.sync_db --mode up

.PHONY: importdb
importdb: ## Import the links database from S3
	python3 -m ingest.sync_db --mode down
	python3 -m ingest.import_db

.PHONY: launch
launch: ## Open the website
	open https://guarded-everglades-89687.herokuapp.com/?aggregator=-Custom

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
