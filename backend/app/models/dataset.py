from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class Dataset(Base):
    """데이터셋 관리 테이블.

    데이터 포털에서 관리하는 데이터셋의 메타 정보를 저장한다.
    """

    __tablename__ = "datasets"
    __table_args__ = {"comment": "데이터셋 관리 테이블"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="PK")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="데이터셋 이름")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="설명")
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="소스 유형 (file, database, api)")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="활성 여부")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="생성 일시"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="수정 일시"
    )
