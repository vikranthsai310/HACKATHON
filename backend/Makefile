# Makefile for HRM Decision System Backend

.PHONY: help install test run clean lint format

help:
	@echo "Available commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make test       - Run unit tests"
	@echo "  make test-full  - Run full system test"
	@echo "  make run        - Start API server"
	@echo "  make clean      - Clean cache files"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black"

install:
	pip install -r requirements.txt

test:
	pytest test_phase1.py -v

test-full:
	python test_system.py

run:
	python -m app.main

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

lint:
	flake8 app/ --max-line-length=120

format:
	black app/ --line-length=120
