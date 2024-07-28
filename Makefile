all: build

build: build-libs
	poetry build

build-libs:
	@make -C libs/*

install: build-libs
	poetry install --only main

install-dev: build-libs
	poetry install --only main,dev
	pre-commit install

lint:
	poetry run ruff check taipan

format:
	poetry run ruff format taipan

test:
	poetry run pytest tests

.PHONY: all build build-libs install install-dev lint format test
