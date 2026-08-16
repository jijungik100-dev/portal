from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """서버 상태 확인 엔드포인트."""
    return {"status": "hello atlas"}
