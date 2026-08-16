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

# backend/frontend가 둘 다 "app"/"tests" 패키지명을 쓰므로 한 pytest 프로세스에서
# 같이 수집하면 모듈명이 충돌한다 (ModuleNotFoundError). 별도 프로세스로 분리 실행한다.
test:
	pytest backend/tests
	pytest frontend/tests

# 단일 테스트 실행: make test-one FILE=backend/tests/test_health.py
test-one:
	pytest $(FILE) -v

# 패턴 매칭 테스트: make test-match PATTERN="test_create"
# exit code 5(수집된 테스트 없음)는 패턴이 해당 쪽에 없다는 뜻이라 실패로 치지 않는다.
test-match:
	pytest backend/tests -k "$(PATTERN)" -v; test $$? -eq 0 -o $$? -eq 5
	pytest frontend/tests -k "$(PATTERN)" -v; test $$? -eq 0 -o $$? -eq 5

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
