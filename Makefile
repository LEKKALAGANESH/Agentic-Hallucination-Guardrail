.PHONY: dev test test-cov test-full test-fast test-golden benchmark lint format clean docker-up docker-down

dev:
	uvicorn src.backend.api:app --reload --port 8000

test:
	pytest src/backend/tests/ -v

test-cov:
	pytest src/backend/tests/ -v --cov=src/backend --cov-report=term-missing

test-full:
	pytest src/backend/tests/ -v --cov=src/backend --cov-report=term-missing --cov-fail-under=80

test-fast:
	pytest src/backend/tests/ -v -m "not slow and not gpu"

test-golden:
	pytest src/backend/tests/test_golden_regression.py -v

benchmark:
	pytest src/backend/tests/test_benchmarks.py -v --benchmark-json=.benchmarks/latest.json

lint:
	ruff check src/backend/

format:
	ruff format src/backend/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	rm -rf .pytest_cache htmlcov .coverage

docker-up:
	docker compose up --build

docker-down:
	docker compose down
