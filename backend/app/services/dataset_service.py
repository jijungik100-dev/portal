from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.schemas.dataset import CreateDatasetRequest, DatasetCountResponse, UpdateDatasetRequest


def get_all(db: Session, page: int = 1, size: int = 20) -> list[Dataset]:
    """데이터셋 목록을 페이지네이션하여 조회한다."""
    offset = (page - 1) * size
    return list(db.query(Dataset).offset(offset).limit(size).all())


def get_by_id(db: Session, dataset_id: int) -> Dataset | None:
    """ID로 데이터셋을 조회한다."""
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()


def create(db: Session, request: CreateDatasetRequest) -> Dataset:
    """데이터셋을 생성한다."""
    dataset = Dataset(
        name=request.name,
        description=request.description,
        source_type=request.source_type,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def update(db: Session, dataset: Dataset, request: UpdateDatasetRequest) -> Dataset:
    """데이터셋을 수정한다."""
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dataset, field, value)
    db.commit()
    db.refresh(dataset)
    return dataset


def delete(db: Session, dataset: Dataset) -> None:
    """데이터셋을 삭제한다."""
    db.delete(dataset)
    db.commit()


def calculate(db: Session) -> DatasetCountResponse:
    """데이터셋 카운트를 계산한다."""
    total = db.query(func.count(Dataset.id)).scalar() or 0
    active = db.query(func.count(Dataset.id)).filter(Dataset.is_active.is_(True)).scalar() or 0
    inactive = total - active
    return DatasetCountResponse(total=total, active=active, inactive=inactive)
