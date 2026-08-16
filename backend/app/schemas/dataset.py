from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateDatasetRequest(BaseModel):
    """데이터셋 생성 요청."""

    name: str
    description: str | None = None
    source_type: str


class UpdateDatasetRequest(BaseModel):
    """데이터셋 수정 요청 (부분 업데이트)."""

    name: str | None = None
    description: str | None = None
    source_type: str | None = None
    is_active: bool | None = None


class DatasetResponse(BaseModel):
    """데이터셋 응답."""

    id: int
    name: str
    description: str | None
    source_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetCountResponse(BaseModel):
    """데이터셋 카운트 응답 (:calculate 결과)."""

    total: int
    active: int
    inactive: int
