# Data Portal

데이터 플랫폼 팀의 데이터 포털 서비스.

## 기술 스택

- **Backend**: FastAPI + SQLAlchemy
- **Frontend**: Streamlit (requests를 통해 Backend API만 호출)
- **Python**: 3.12+
- **DB**: SQLite (local) / MySQL (dev, prod)
- **설정 관리**: YAML 프로파일 (`config/application-{profile}.yml`)
- **Repository**: https://github.travel-wallet.com/Data-platform/data-portal

## 프로젝트 구조

```
data-portal/
├── backend/            # FastAPI 서버
│   ├── app/
│   │   ├── main.py         # 진입점
│   │   ├── config.py       # YAML 설정 로딩
│   │   ├── database.py     # SQLAlchemy engine/session
│   │   ├── dependencies.py # FastAPI Depends (get_db, get_settings)
│   │   ├── routers/        # API 라우터 (도메인별)
│   │   ├── services/       # 비즈니스 로직
│   │   ├── models/         # ORM 모델
│   │   └── schemas/        # Pydantic 스키마
│   └── tests/
├── frontend/           # Streamlit UI
│   ├── app/
│   │   ├── main.py         # 진입점
│   │   ├── api_client.py   # Backend 호출 (유일한 통신 경로)
│   │   ├── pages/          # 멀티페이지
│   │   └── components/     # 재사용 UI 컴포넌트
│   └── tests/
├── config/             # 환경별 YAML 설정
│   ├── application-sample.yml
│   ├── application-local.yml
│   ├── application-dev.yml
│   └── application-prod.yml
├── pyproject.toml      # ruff, mypy, pytest 설정
├── Makefile            # 공통 명령어
└── AGENTS.md           # AI 에이전트 규칙
```

## 아키텍처

```
브라우저 → Streamlit (Frontend) → requests → FastAPI (Backend) → SQLAlchemy → DB
```

- Frontend는 순수 UI 레이어로만 사용 (DB 직접 접근 금지)
- 모든 Backend 통신은 `api_client.py`를 통해서만 수행
- 설정은 YAML 프로파일로 관리 (sample, local, dev, prod)

### API 라우팅 정책

| 구분 | prefix 패턴 | 용도 |
|------|-------------|------|
| 백오피스 API | `/admin/...` | 프론트엔드(백오피스) 전용 |
| 외부 API | `/api/v{version}/...` | 외부 시스템 연동용 |

### 현재 구현된 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/health` | 서버 상태 확인 (`{"status": "hello atlas"}`) |
| GET | `/admin/home` | 홈 메시지 반환 (`Hello Atlas`) |

## 로컬 실행 방법

### 1. 환경 설정

```bash
# venv 생성 및 활성화
python -m venv .venv
source .venv/bin/activate

# 의존성 설치
make install
```

### 2. 서버 실행 (터미널 2개)

```bash
# 터미널 1: Backend (port 8000)
APP_PROFILE=local make run-backend

# 터미널 2: Frontend (port 8501)
make run-frontend
```

### 3. 접속

- Frontend: http://localhost:8501
- Backend API 문서: http://localhost:8000/docs

## 개발 명령어

```bash
make lint             # 린트 검사
make format           # 자동 포맷팅
make type-check       # 타입 검사
make test             # 전체 테스트
make test-one FILE=backend/tests/test_health.py   # 단일 테스트
make clean            # 캐시 정리
```

## Git Workflow (GitHub Flow)

- `main` 브랜치는 항상 배포 가능 상태 유지 — `main`에 직접 push 금지
- 모든 작업은 `main`에서 feature branch를 생성하여 진행
- 브랜치 네이밍은 커밋 컨벤션 prefix와 동일: `feat/xxx`, `fix/xxx`, `refactor/xxx`, `docs/xxx`, `test/xxx`, `chore/xxx`
- 작업 완료 시 Pull Request 생성
- PR 머지 시 **squash merge** 사용 (PR당 커밋 1개)
- 머지 후 feature branch 삭제

## 커밋 컨벤션

형식: `prefix: 설명`

| prefix | 코드 동작 변경? | 예시 |
|--------|---------------|------|
| `feat` | O (새 기능) | 새 API 엔드포인트 추가 |
| `fix` | O (버그 수정) | 잘못된 응답값 수정 |
| `refactor` | X (동작 동일, 코드 구조 변경) | 함수 분리, 변수명 변경 |
| `chore` | X (코드 자체 안 건드림) | Makefile 수정, 의존성 추가 |
| `docs` | X | README 업데이트 |
| `test` | X | 테스트 추가 |

## 작업 이력

### 초기 셋업 (2026-08-13)

- FastAPI + Streamlit 프로젝트 scaffolding 구성
- YAML 프로파일 기반 설정 관리 (sample, local, dev, prod)
- SQLAlchemy DB 연결 (SQLite/MySQL)
- Health check 엔드포인트 (`GET /health` → `"hello atlas"`)
- Home 엔드포인트 (`GET /admin/home` → `"Hello Atlas"`)
- Frontend에서 Backend 연결 상태 표시 및 홈 메시지 출력
- CommonResponse 포맷 적용 (code, message, data 구조)
- Ruff + mypy + pytest 개발 도구 설정
- pre-commit hook 설정
- AGENTS.md / AGENTS_KR.md AI 에이전트 규칙 문서 작성
- GitHub Flow 기반 Git 워크플로우 수립
