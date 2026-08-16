from fastapi import APIRouter

from app.schemas.common import CommonResponse

router = APIRouter(prefix="/admin", tags=["home"])


@router.get("/home", response_model=CommonResponse[dict[str, str]])
def get_home_message() -> CommonResponse[dict[str, str]]:
    """홈 메시지 반환."""
    return CommonResponse(data={"message": "Hello Atlas"})
