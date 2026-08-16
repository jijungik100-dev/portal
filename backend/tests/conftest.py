import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import BigInteger, create_engine, event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.dependencies import get_db
from app.main import app
from app.models import Base

# 테스트는 항상 sample 프로파일 사용
os.environ["APP_PROFILE"] = "sample"


# SQLite에서 BigInteger를 INTEGER로 렌더링하여 autoincrement 호환 처리
@compiles(BigInteger, "sqlite")
def _compile_big_int_sqlite(type_, compiler, **kw):  # type: ignore[no-untyped-def]
    return "INTEGER"


@pytest.fixture(scope="session")
def engine():  # type: ignore[no-untyped-def]
    """테스트용 SQLite in-memory 엔진."""
    _engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, connection_record):  # type: ignore[no-untyped-def]
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=_engine)
    yield _engine
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def db(engine) -> Generator[Session, None, None]:  # type: ignore[no-untyped-def]
    """테스트용 DB 세션 (각 테스트마다 테이블 데이터 초기화)."""
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()
        # 각 테스트 후 모든 테이블 데이터 삭제
        with engine.connect() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(table.delete())
            conn.commit()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient (DB 세션 오버라이드)."""

    def _override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
