<!-- 이 파일은 AGENTS.md (영문 버전)와 동기화됩니다. 한쪽을 수정하면 반드시 다른 쪽도 업데이트할 것. -->

# AGENTS.md

이 파일은 AI 코딩 에이전트(opencode, claude code 등)가 이 저장소에서 작업할 때 따라야 할 규칙입니다.

## 프로젝트 개요

- **프로젝트**: Data Portal (데이터 포털)
- **기술 스택**: FastAPI (backend) + Streamlit (frontend)
- **Python**: 3.12+
- **아키텍처**: Monorepo (`backend/`, `frontend/` 분리)
- **설정 관리**: YAML 프로파일 (`config/application-{profile}.yml`)
- **DB**: SQLAlchemy (local=SQLite/MySQL, dev/prod=MySQL)

## 환경

- 내부망 (인터넷 접근 불가)
- Enterprise GitHub: github.travel-wallet.com

## 프로젝트 구조

```
data-portal/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 진입점
│   │   ├── config.py        # YAML 기반 Settings 로딩
│   │   ├── database.py      # SQLAlchemy engine/session
│   │   ├── dependencies.py  # FastAPI Depends (get_db, get_settings)
│   │   ├── models/          # SQLAlchemy ORM 모델
│   │   ├── schemas/         # Pydantic request/response 스키마
│   │   ├── routers/         # API 라우터 (도메인별 분리)
│   │   └── services/        # 비즈니스 로직
│   └── tests/
├── frontend/
│   ├── app/
│   │   ├── main.py          # Streamlit 진입점
│   │   ├── api_client.py    # requests 기반 backend 호출 (유일한 통신 경로)
│   │   ├── pages/           # Streamlit 멀티페이지
│   │   └── components/      # 재사용 UI 컴포넌트
│   └── tests/
├── config/                   # 환경별 설정 (application-{profile}.yml)
├── pyproject.toml            # ruff, mypy, pytest 통합 설정
├── Makefile                  # 공통 명령어
└── requirements-dev.txt      # 개발 도구
```

## 코드 스타일 규칙

### Formatter (Ruff)

- **line-length**: 120
- **quote**: double quote (`"`)
- **indent**: 4 spaces
- **trailing comma**: 멀티라인 구조에서 사용

### Imports (isort via Ruff)

```python
# 1. 표준 라이브러리
import os
from pathlib import Path

# 2. 서드파티
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. 프로젝트 내부
from app.config import get_settings
from app.dependencies import get_db
```

### 타입 힌트

- 모든 함수 시그니처에 타입 힌트 **필수** (mypy `disallow_untyped_defs`)
- 내부 변수는 타입 추론에 맡겨도 됨
- `Any` 사용 최소화, 반환 타입에 `Any` 금지

```python
# Good
def get_user(user_id: int, db: Session) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


# Bad - 타입 힌트 없음
def get_user(user_id, db):
    return db.query(User).filter(User.id == user_id).first()
```

### 네이밍

| 대상 | 규칙 | 예시 |
|------|------|------|
| 파일/모듈 | snake_case | `user_service.py` |
| 클래스 | PascalCase | `UserService`, `CreateUserRequest` |
| 함수/변수 | snake_case | `get_user_by_id`, `is_active` |
| 상수 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE` |
| API 라우터 | 도메인명 복수형 | `routers/users.py`, `routers/datasets.py` |

### 에러 처리

evidence-pack 패턴을 따름:

```python
# 1. 건별 처리 시 - 개별 에러는 잡고, 결과 집계
results = {"success": 0, "fail": 0, "failures": []}
for item in items:
    try:
        process(item)
        results["success"] += 1
    except Exception as e:
        results["fail"] += 1
        results["failures"].append({"id": item.id, "error": str(e)})
        logger.exception(f"Failed to process item {item.id}")

# 2. FastAPI 라우터에서 - HTTPException 사용
from fastapi import HTTPException


def get_user(user_id: int) -> User:
    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 3. 치명적 에러 - 즉시 중단
if critical_condition:
    logger.error("FATAL: ...")
    raise SystemExit(1)
```

## 아키텍처 규칙

### Backend (FastAPI)

- **레이어 구조**: Router → Service → Model (단방향 의존)
- Router: HTTP 요청/응답 처리만, 비즈니스 로직 금지
- Service: 비즈니스 로직, DB 접근은 SQLAlchemy Session 사용
- Model: 테이블 정의만, 로직 금지
- Schema: Pydantic 모델로 request/response 정의 (ORM 모델과 분리)

### Frontend (Streamlit)

- **Backend 호출은 반드시 `api_client.py`를 통해서만** (requests 사용)
- 직접 DB 접근 금지, 직접 import 금지
- 순수 UI 레이어로만 사용

### API 라우팅 정책

두 종류의 API가 존재하며, prefix로 구분한다:

| 구분 | prefix 패턴 | 인증 방식 | 버전 관리 | 용도 |
|------|-------------|-----------|-----------|------|
| 백오피스 API | `/admin/...` | JWT 로그인 인증 | 버전 없음 | 프론트엔드(백오피스) 전용 |
| 외부 API | `/api/v{version}/...` | APP_KEY 인증 | 버전 필수 | 외부 시스템 연동용 |

**URL 예시:**
- 백오피스: `/admin/home`, `/admin/users`, `/admin/users/{id}`
- 외부 API: `/api/v1.0/datasets`, `/api/v1.0/datasets/{id}`

**URL 네이밍:**
- 리소스명은 복수형 명사 사용 (`/users`, `/datasets`)
- 두 단어 이상의 리소스명은 하이픈(`-`)으로 연결: `/collected-datasets`, `/api-keys`, `/maximum-balance`

**Custom Method (비-CRUD 동작):**

리소스에 대한 특수 동작은 Custom Method 패턴을 사용한다 (참고: Google AIP-136):

- 형식: `POST /resource:verb` 또는 `POST /resource/{id}:verb`
- HTTP 메서드: 항상 `POST`
- 리소스 URL 끝에 콜론(`:`) + 동사를 붙인다

| 동사 | 의미 | 예시 |
|------|------|------|
| `cancel` | 취소 | `POST /orders/{orderId}:cancel` |
| `activate` | 활성화 | `POST /subscriptions/{subId}:activate` |
| `deactivate` | 비활성화 | `POST /subscriptions/{subId}:deactivate` |
| `approve` | 승인 | `POST /requests/{reqId}:approve` |
| `reject` | 거절 | `POST /requests/{reqId}:reject` |
| `import` | 데이터 가져오기 | `POST /users:import` |
| `export` | 데이터 내보내기 | `POST /reports:export` |
| `search` | 복잡한 검색 | `POST /posts:search` |
| `check` | 검증/확인 | `POST /coupons:check` |

**규칙:**
- 백오피스 API (`/admin`)는 내부 프론트엔드만 호출 — 버전 불필요
- 외부 API (`/api/v{version}`)는 외부 시스템이 호출 — Breaking change 시 새 버전 추가 (기존 버전 유지)
- 새 API 추가 시 반드시 위 구분에 맞는 prefix를 사용할 것
- 하나의 엔드포인트가 두 prefix에 동시에 노출되면 안 됨

### Config (YAML 프로파일)

- `config/application-{profile}.yml`에 모든 설정 기재 (시크릿 포함)
- 프로파일: `sample`, `local`, `dev`, `prod`
- `APP_PROFILE` 환경변수 또는 `--profile` 인자로 선택
- `application-my-local.yml`은 개인용 (gitignore 처리됨)

## Git 워크플로우 (GitHub Flow)

- `main` 브랜치는 항상 배포 가능 상태 유지 — `main`에 직접 push 금지
- 모든 작업은 `main`에서 feature branch를 생성하여 진행
- 브랜치 네이밍은 커밋 컨벤션 prefix와 동일: `feat/xxx`, `fix/xxx`, `refactor/xxx`, `docs/xxx`, `test/xxx`, `chore/xxx`
- 작업 완료 시 Pull Request 생성
- PR 머지 시 **squash merge** 사용 (PR당 커밋 1개)
- 머지 후 feature branch 삭제

## 커밋 컨벤션

```
feat: 새로운 기능 추가
fix: 버그 수정
refactor: 리팩토링 (기능 변경 없음)
docs: 문서 수정
test: 테스트 추가/수정
chore: 빌드, 설정 변경
```

## AI 에이전트 작업 절차

AI 에이전트가 코드 작업 시 따라야 할 절차:

1. **코드 작성 전** — 기존 코드베이스의 패턴/구조를 먼저 파악하고, 동일한 컨벤션을 따를 것
2. **한 번에 하나의 관심사만 변경** — 여러 파일을 동시에 리팩토링하지 말 것
3. **새 API 엔드포인트 추가 시** — Router → Service → Schema → Test 순서로 작성
4. **작업 완료 후** — lint → type-check → test 순서로 검증 실행 (모두 통과 확인)
5. **불확실하면 먼저 물어볼 것** — 아키텍처 변경, 새 패키지 추가, 대규모 리팩토링은 사전 확인 필수

## AI 에이전트 금지사항

- 시크릿/비밀번호를 코드에 하드코딩하지 말 것 (YAML config에만 기재)
- `config/application-my-local.yml` 파일을 생성하거나 커밋하지 말 것
- frontend에서 backend 내부 모듈을 직접 import하지 말 것
- `Any` 타입을 함수 반환 타입으로 사용하지 말 것
- 테스트 없이 새 API 엔드포인트를 추가하지 말 것
- 기존 YAML config 구조를 .env 방식으로 변경하지 말 것
- 기존 디렉토리 구조나 아키텍처를 대규모로 변경하지 말 것 (사전 합의 없이)
- 여러 파일을 한꺼번에 리팩토링하지 말 것 (한 번에 하나의 관심사만 변경)
- `/admin` API와 `/api` API의 prefix 구분을 임의로 변경하지 말 것
- `AGENTS.md` 또는 `AGENTS_KR.md`를 수정할 때 반드시 다른 쪽 파일도 동기화할 것
