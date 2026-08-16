from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """모든 ORM 모델의 기본 클래스."""

    pass


# 모든 모델을 여기서 import하여 Base.metadata에 등록한다.
from app.models.dataset import Dataset  # noqa: E402, F401
