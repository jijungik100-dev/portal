from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    """DB 세션 의존성."""
    yield from _get_db()


def get_current_settings(settings: Settings = Depends(get_settings)) -> Settings:
    """Settings 의존성 (테스트 시 오버라이드 가능)."""
    return settings
