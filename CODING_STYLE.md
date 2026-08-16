# Coding Style Guide

이 문서는 프로젝트 코드 작성 시 따르는 스타일 가이드입니다.
컨벤션/린터 규칙은 `AGENTS.md` 참조. 여기는 **"어떻게 코드를 작성하는가"**에 집중합니다.

---

## if 처리 — Guard Clause 패턴

Early return / early raise를 적극 사용한다. 정상 흐름은 들여쓰기를 최소로 유지한다.

```python
# Router — 조건 불충분 시 즉시 HTTPException
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> CommonResponse[UserResponse]:
    user = user_service.find_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return CommonResponse(data=UserResponse.model_validate(user))


# Service — 유효하지 않으면 None 반환 또는 ValueError raise
def find_active_user(db: Session, user_id: int) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    if not user.is_active:
        return None
    return user


# 반복문 내부 — continue로 빠르게 건너뜀
for row in rows:
    if row["status"] is None:
        logger.info(f"[import] skip: id={row['id']} - status is NULL")
        skip_count += 1
        continue

    if row["type"] not in VALID_TYPES:
        logger.info(f"[import] skip: id={row['id']} - unknown type '{row['type']}'")
        skip_count += 1
        continue

    process(row)
    success_count += 1
```

---

## 줄바꿈 기준

- 논리적 블록 사이: 빈 줄 **1개**
- 함수 사이: 빈 줄 **2개**
- 함수 내부: 단계별로 빈 줄 + 주석으로 구분

```python
def create_dataset(db: Session, request: CreateDatasetRequest) -> Dataset:
    # 1. 유효성 검증
    existing = get_by_name(db, request.name)
    if existing:
        raise ValueError(f"Dataset name already exists: {request.name}")

    # 2. 생성
    dataset = Dataset(**request.model_dump())
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # 3. 후처리
    logger.info(f"[dataset] created: id={dataset.id}, name={dataset.name}")
    return dataset
```

---

## 섹션 구분 주석

파일 내 논리 블록이 여러 개일 때 `# --- 섹션명 ---` 형태로 구분한다.

```python
# --- Constants ---
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20

# --- Query helpers ---
def build_filter_query(db: Session, filters: dict) -> Query:
    ...

# --- CRUD ---
def get_all(db: Session, page: int, size: int) -> list[Dataset]:
    ...

def create(db: Session, request: CreateDatasetRequest) -> Dataset:
    ...
```

---

## 문자열 포맷팅

f-string만 사용한다. `.format()`이나 `%` 연산자는 사용하지 않는다.

```python
# Good
logger.info(f"[user] created: id={user.id}, name={user.name}")
url = f"{base_url}/api/v1.0/datasets/{dataset_id}"

# Bad
logger.info("[user] created: id={}, name={}".format(user.id, user.name))
logger.info("[user] created: id=%s, name=%s" % (user.id, user.name))
```

---

## 로깅

context prefix를 명시한다: `[도메인]` 또는 `[도메인/상세]`

```python
logger.info(f"[user] created: id={user.id}")
logger.info(f"[dataset] updated: id={dataset.id}, fields={changed_fields}")
logger.warning(f"[auth/jwt] token expired: user_id={user_id}")
logger.error(f"[payment] failed: order_id={order_id} - {error}")
```

---

## 함수 설계

하나의 함수 = 하나의 책임. 복잡한 로직은 작은 유틸 함수로 분리한다.

```python
# Bad — 하나의 함수에 여러 책임
def process_order(db: Session, order_id: int) -> dict:
    order = db.query(Order).filter(Order.id == order_id).first()
    # 50줄의 검증 로직...
    # 30줄의 결제 로직...
    # 20줄의 알림 로직...
    return result


# Good — 책임별 분리
def process_order(db: Session, order_id: int) -> dict:
    order = _get_order_or_raise(db, order_id)
    _validate_order(order)
    payment_result = _execute_payment(order)
    _send_notification(order, payment_result)
    return payment_result


def _get_order_or_raise(db: Session, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError(f"Order not found: {order_id}")
    return order
```

---

## 에러 처리 (웹서비스)

계층별로 에러 처리 방식이 다르다:

```python
# --- Router 계층: HTTPException ---
@router.post("")
def create_user(request: CreateUserRequest, db: Session = Depends(get_db)) -> CommonResponse[UserResponse]:
    try:
        user = user_service.create(db, request)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return CommonResponse(data=UserResponse.model_validate(user))


# --- Service 계층: None 반환 또는 ValueError raise ---
def create(db: Session, request: CreateUserRequest) -> User:
    existing = find_by_email(db, request.email)
    if existing:
        raise ValueError(f"Email already exists: {request.email}")

    user = User(**request.model_dump())
    db.add(user)
    db.commit()
    return user


def find_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


# --- 배치/벌크 작업: 건별 try/except + 결과 집계 ---
def bulk_import(db: Session, items: list[dict]) -> dict:
    results = {"success": 0, "fail": 0, "failures": []}

    for item in items:
        try:
            _import_single(db, item)
            results["success"] += 1
        except Exception as e:
            results["fail"] += 1
            results["failures"].append({"id": item.get("id"), "error": str(e)})
            logger.warning(f"[import] failed: id={item.get('id')} - {e}")

    return results
```

---

## 서비스 함수 반환 패턴

| 동작 | 반환값 | 라우터에서 처리 |
|------|--------|----------------|
| 단일 조회 | `T \| None` | None이면 404 raise |
| 목록 조회 | `list[T]` (빈 리스트 가능) | 그대로 반환 |
| 생성 | `T` (생성된 객체) | 201 + 객체 반환 |
| 수정 | `T` (수정된 객체) | 200 + 객체 반환 |
| 삭제 | `None` | 204 No Content |

```python
# Service
def get_by_id(db: Session, dataset_id: int) -> Dataset | None:
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()

def get_all(db: Session, page: int, size: int) -> list[Dataset]:
    offset = (page - 1) * size
    return db.query(Dataset).offset(offset).limit(size).all()

def create(db: Session, request: CreateDatasetRequest) -> Dataset:
    dataset = Dataset(**request.model_dump())
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset

def delete(db: Session, dataset: Dataset) -> None:
    db.delete(dataset)
    db.commit()
```
