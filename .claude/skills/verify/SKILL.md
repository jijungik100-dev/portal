---
name: verify
description: Run lint (ruff), type-check (mypy), and tests (pytest) for the Data Portal project in order, and report a pass/fail evidence pack. Use after making code changes and before declaring work done — operationalizes AGENTS.md's required "lint → type-check → test" step.
---

# /verify — Data Portal 검증

`AGENTS.md`의 AI Agent Workflow 4번 규칙("완료 후 — 검증을 순서대로 실행: lint → type-check → test (모두 통과 확인)")을 그대로 실행하는 skill이다. 코드 작업을 "완료"라고 보고하기 전에는 반드시 이 skill을 실행한다.

## 실행 절차

**순서를 지킨다. 앞 단계가 실패하면 뒤 단계는 실행하지 않고 그 자리에서 멈춘다** (AGENTS.md가 명시한 순서이자, 빠른 실패로 불필요한 실행을 줄이기 위함).

1. `make lint` (`ruff check .`) 실행
2. 통과 시 `make type-check` (`mypy backend/app`) 실행
3. 통과 시 `make test` (`pytest`) 실행

각 명령은 Bash 도구로 프로젝트 루트에서 실행한다.

## 결과 보고 (evidence-pack 형식)

`AGENTS.md`의 에러 처리 컨벤션(건별 결과 집계) 방식을 그대로 따라 아래처럼 보고한다:

```
lint:       ✅ pass | ❌ fail
type-check: ✅ pass | ❌ fail | ⏭️ skipped (lint 실패로 인해 미실행)
test:       ✅ pass | ❌ fail | ⏭️ skipped (이전 단계 실패로 인해 미실행)
```

- 실패한 단계가 있으면 **그 단계의 실제 에러 출력을 요약하지 말고 원문 그대로** 인용해서 보여준다.
- 절대 "사소한 실패니 넘어가겠다"고 판단하지 않는다 — 세 단계가 모두 통과하기 전까지 작업은 끝난 것이 아니다.
- `ruff check`가 `--fix`로 자동 수정 가능한 이슈를 보고하면, 임의로 코드를 고치지 말고 어떤 파일을 어떻게 고칠지 먼저 알리고 사용자 확인 후 `ruff format .` / `ruff check --fix .`를 적용한다.
- `mypy`나 `pytest` 실패는 자동으로 고치려 하지 말고, 원인과 관련 파일(`file:line`)을 짚어서 보고한다. 수정은 별도로 진행한다.

## 언제 쓰나

- 백엔드(`backend/app`, `backend/tests`) 또는 프론트엔드(`frontend/app`) 코드를 수정한 직후
- 새 엔드포인트(Router → Service → Schema → Model → Test)를 다 만든 직후
- PR을 올리기 직전 최종 확인
- 세 단계 모두 ✅가 아니면, 사용자에게 "작업 완료"라고 보고하지 않는다.
