.DEFAULT_GOAL := help

.PHONY: run
run: ## Run Django
	poetry run python manage.py runserver

.PHONY: migrate
migrate: ## Run Django migrations
	poetry run python manage.py makemigrations && poetry run python manage.py migrate

.PHONY: poetry-setup
poetry-setup: ## Install Python deps
	pip install poetry
	poetry install

.PHONY: setup ## Install Homebrew and Python deps
setup: poetry-setup

.PHONY: build
build: ## Build package
	poetry build

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
