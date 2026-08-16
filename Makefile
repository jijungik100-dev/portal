.PHONY: install lint format type-check test test-one run-backend run-frontend clean

# ============================================================
# Setup
# ============================================================

install:
	pip install -r requirements-dev.txt
	pip install -r backend/requirements.txt
	pip install -r frontend/requirements.txt
	pre-commit install

# ============================================================
# Code Quality
# ============================================================

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

type-check:
	mypy backend/app

# ============================================================
# Testing
# ============================================================

test:
	pytest

# 단일 테스트 실행: make test-one FILE=backend/tests/test_health.py
test-one:
	pytest $(FILE) -v

# 패턴 매칭 테스트: make test-match PATTERN="test_create"
test-match:
	pytest -k "$(PATTERN)" -v

# ============================================================
# Run
# ============================================================

run-backend:
	cd backend && PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && PYTHONPATH=. streamlit run app/main.py --server.port 8501

# ============================================================
# Utility
# ============================================================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
