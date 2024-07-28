all: build

build:
	poetry build
	poetry run pip install dist/taipan-*.whl

install:
	poetry install --only main

install-dev:
	poetry install --only main,dev
	pre-commit install

lint:
	poetry run ruff check taipan

format:
	poetry run ruff format taipan

type-check:
	poetry run pyright taipan

test:
	poetry run pytest tests

.PHONY: all build install install-dev lint format type-check test
