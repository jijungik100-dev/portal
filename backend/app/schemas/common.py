from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class CommonResponse(BaseModel, Generic[T]):
    """API 공통 응답 envelope.

    모든 API 응답은 이 포맷을 따른다.
    - code: 0이면 성공, 그 외는 에러 코드
    - message: 응답 메시지 (에러 시 사용자 노출 메시지)
    - data: 실제 응답 데이터 (없으면 None)
    """

    code: int = 0
    message: str = "OK"
    data: T | None = None
