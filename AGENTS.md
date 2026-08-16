<!-- This file is synced with AGENTS_KR.md (Korean version). Update both when making changes. -->

# AGENTS.md

Rules for AI coding agents (opencode, claude code, etc.) working in this repository.

## Project Overview

- **Project**: Data Portal
- **Tech Stack**: FastAPI (backend) + Streamlit (frontend)
- **Python**: 3.12+
- **Architecture**: Monorepo (`backend/`, `frontend/` separated)
- **Config Management**: YAML profiles (`config/application-{profile}.yml`)
- **DB**: SQLAlchemy (local=SQLite/MySQL, dev/prod=MySQL)

## Environment

- Internal network (no internet access)
- Enterprise GitHub: github.travel-wallet.com

## Project Structure

```
data-portal/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entrypoint
│   │   ├── config.py        # YAML-based Settings loader
│   │   ├── database.py      # SQLAlchemy engine/session
│   │   ├── dependencies.py  # FastAPI Depends (get_db, get_settings)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # API routers (separated by domain)
│   │   └── services/        # Business logic
│   └── tests/
├── frontend/
│   ├── app/
│   │   ├── main.py          # Streamlit entrypoint
│   │   ├── api_client.py    # requests-based backend calls (sole communication path)
│   │   ├── pages/           # Streamlit multi-page
│   │   └── components/      # Reusable UI components
│   └── tests/
├── config/                   # Environment-specific settings (application-{profile}.yml)
├── pyproject.toml            # ruff, mypy, pytest unified config
├── Makefile                  # Common commands
└── requirements-dev.txt      # Dev tools
```

## Code Style Rules

### Formatter (Ruff)

- **line-length**: 120
- **quote**: double quote (`"`)
- **indent**: 4 spaces
- **trailing comma**: use in multiline structures

### Imports (isort via Ruff)

```python
# 1. Standard library
import os
from pathlib import Path

# 2. Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# 3. Project internal
from app.config import get_settings
from app.dependencies import get_db
```

### Type Hints

- Type hints are **required** on all function signatures (mypy `disallow_untyped_defs`)
- Internal variables can rely on type inference
- Minimize `Any` usage; `Any` is forbidden as a return type

```python
# Good
def get_user(user_id: int, db: Session) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


# Bad - no type hints
def get_user(user_id, db):
    return db.query(User).filter(User.id == user_id).first()
```

### Naming

| Target | Convention | Example |
|--------|-----------|---------|
| File/Module | snake_case | `user_service.py` |
| Class | PascalCase | `UserService`, `CreateUserRequest` |
| Function/Variable | snake_case | `get_user_by_id`, `is_active` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE` |
| API Router | plural domain name | `routers/users.py`, `routers/datasets.py` |

### Error Handling

Follow the evidence-pack pattern:

```python
# 1. Batch processing - catch individual errors, aggregate results
results = {"success": 0, "fail": 0, "failures": []}
for item in items:
    try:
        process(item)
        results["success"] += 1
    except Exception as e:
        results["fail"] += 1
        results["failures"].append({"id": item.id, "error": str(e)})
        logger.exception(f"Failed to process item {item.id}")

# 2. In FastAPI routers - use HTTPException
from fastapi import HTTPException


def get_user(user_id: int) -> User:
    user = user_service.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 3. Fatal errors - abort immediately
if critical_condition:
    logger.error("FATAL: ...")
    raise SystemExit(1)
```

## Architecture Rules

### Backend (FastAPI)

- **Layer structure**: Router → Service → Model (unidirectional dependency)
- Router: HTTP request/response handling only, no business logic
- Service: Business logic, DB access via SQLAlchemy Session
- Model: Table definitions only, no logic
- Schema: Pydantic models for request/response (separated from ORM models)

### Frontend (Streamlit)

- **All backend calls must go through `api_client.py` only** (using requests)
- No direct DB access, no direct imports from backend
- Pure UI layer only

### API Routing Policy

Two types of APIs exist, distinguished by prefix:

| Type | Prefix Pattern | Auth Method | Versioning | Purpose |
|------|---------------|-------------|------------|---------|
| Backoffice API | `/admin/...` | JWT login auth | No version | Frontend (backoffice) only |
| External API | `/api/v{version}/...` | APP_KEY auth | Version required | External system integration |

**URL examples:**
- Backoffice: `/admin/home`, `/admin/users`, `/admin/users/{id}`
- External API: `/api/v1.0/datasets`, `/api/v1.0/datasets/{id}`

**URL Naming:**
- Use plural nouns for resources (`/users`, `/datasets`)
- Multi-word resource names use hyphen (`-`) as separator: `/collected-datasets`, `/api-keys`, `/maximum-balance`

**Custom Method (non-CRUD actions):**

Use Custom Method pattern for special actions on resources (ref: Google AIP-136):

- Format: `POST /resource:verb` or `POST /resource/{id}:verb`
- HTTP method: always `POST`
- Append colon (`:`) + verb at the end of the resource URL

| Verb | Meaning | Example |
|------|---------|---------|
| `cancel` | Cancel | `POST /orders/{orderId}:cancel` |
| `activate` | Activate | `POST /subscriptions/{subId}:activate` |
| `deactivate` | Deactivate | `POST /subscriptions/{subId}:deactivate` |
| `approve` | Approve | `POST /requests/{reqId}:approve` |
| `reject` | Reject | `POST /requests/{reqId}:reject` |
| `import` | Import data | `POST /users:import` |
| `export` | Export data | `POST /reports:export` |
| `search` | Complex search | `POST /posts:search` |
| `check` | Validate/check | `POST /coupons:check` |

**Rules:**
- Backoffice API (`/admin`) is called only by internal frontend — no versioning needed
- External API (`/api/v{version}`) is called by external systems — add new version on breaking changes (keep existing versions)
- New APIs must use the appropriate prefix based on the above classification
- A single endpoint must not be exposed under both prefixes

### Config (YAML Profiles)

- All settings stored in `config/application-{profile}.yml` (including secrets)
- Profiles: `sample`, `local`, `dev`, `prod`
- Selected via `APP_PROFILE` env var or `--profile` argument
- `application-my-local.yml` is personal (gitignored)

## Git Workflow (GitHub Flow)

- `main` branch is always deployable — do not push directly to `main`
- Create a feature branch from `main` for all work
- Branch naming follows commit convention prefix: `feat/xxx`, `fix/xxx`, `refactor/xxx`, `docs/xxx`, `test/xxx`, `chore/xxx`
- Open a Pull Request when work is ready for review
- Use **squash merge** to merge PRs into `main` (one commit per PR)
- Delete the feature branch after merge

## Commit Convention

```
feat: Add new feature
fix: Bug fix
refactor: Refactoring (no behavior change)
docs: Documentation update
test: Add/update tests
chore: Build, config changes
```

## AI Agent Workflow

Steps AI agents must follow when working on code:

1. **Before writing code** — Explore existing codebase patterns/structure first, then follow the same conventions
2. **One concern at a time** — Do not refactor multiple files simultaneously
3. **Adding a new API endpoint** — Create in order: Router → Service → Schema → Test
4. **After completing work** — Run verification in order: lint → type-check → test (ensure all pass)
5. **When uncertain, ask first** — Architecture changes, new package additions, large-scale refactoring require prior confirmation

## AI Agent Restrictions

- Do not hardcode secrets/passwords in code (use YAML config only)
- Do not create or commit `config/application-my-local.yml`
- Do not directly import backend internal modules from frontend
- Do not use `Any` as a function return type
- Do not add new API endpoints without tests
- Do not convert existing YAML config structure to .env approach
- Do not make large-scale changes to existing directory structure or architecture (without prior agreement)
- Do not refactor multiple files at once (change only one concern at a time)
- Do not arbitrarily change the `/admin` vs `/api` prefix distinction
- When modifying `AGENTS.md` or `AGENTS_KR.md`, always sync the other file
