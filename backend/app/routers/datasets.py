from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.common import CommonResponse
from app.schemas.dataset import (
    CreateDatasetRequest,
    DatasetCountResponse,
    DatasetResponse,
    UpdateDatasetRequest,
)
from app.services import dataset_service

router = APIRouter(prefix="/api/v1.0/datasets", tags=["datasets"])


@router.get("", response_model=CommonResponse[list[DatasetResponse]])
def list_datasets(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
) -> CommonResponse[list[DatasetResponse]]:
    """데이터셋 목록 조회 (페이지네이션)."""
    datasets = dataset_service.get_all(db, page=page, size=size)
    return CommonResponse(data=[DatasetResponse.model_validate(d) for d in datasets])


@router.get("/{dataset_id}", response_model=CommonResponse[DatasetResponse])
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
) -> CommonResponse[DatasetResponse]:
    """데이터셋 단건 조회."""
    dataset = dataset_service.get_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return CommonResponse(data=DatasetResponse.model_validate(dataset))


@router.post("", response_model=CommonResponse[DatasetResponse], status_code=201)
def create_dataset(
    request: CreateDatasetRequest,
    db: Session = Depends(get_db),
) -> CommonResponse[DatasetResponse]:
    """데이터셋 생성."""
    dataset = dataset_service.create(db, request)
    return CommonResponse(data=DatasetResponse.model_validate(dataset))


@router.put("/{dataset_id}", response_model=CommonResponse[DatasetResponse])
def update_dataset(
    dataset_id: int,
    request: UpdateDatasetRequest,
    db: Session = Depends(get_db),
) -> CommonResponse[DatasetResponse]:
    """데이터셋 수정."""
    dataset = dataset_service.get_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    updated = dataset_service.update(db, dataset, request)
    return CommonResponse(data=DatasetResponse.model_validate(updated))


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
) -> None:
    """데이터셋 삭제."""
    dataset = dataset_service.get_by_id(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dataset_service.delete(db, dataset)


@router.post(":calculate", response_model=CommonResponse[DatasetCountResponse])
def calculate_datasets(
    db: Session = Depends(get_db),
) -> CommonResponse[DatasetCountResponse]:
    """데이터셋 카운트 계산 (Custom method)."""
    result = dataset_service.calculate(db)
    return CommonResponse(data=result)
