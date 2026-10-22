PYTHON ?= python3.11
VENV := .venv/bin
.PHONY: install test backend-test frontend-test api web build
install:
	$(PYTHON) -m venv .venv
	$(VENV)/python -m pip install -r requirements.txt 'pytest-bdd>=6.1.1,<9' pytest-cov pytest-timeout requests-mock
	cd frontend && npm ci
backend-test:
	AWS_EC2_METADATA_DISABLED=true $(VENV)/python -m pytest backend/tests tests/test_*.py -q
frontend-test:
	cd frontend && npm run test:ci
test: backend-test frontend-test
api:
	$(VENV)/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
web:
	cd frontend && npm start
build:
	cd frontend && npm run build
