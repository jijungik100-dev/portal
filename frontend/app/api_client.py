"""Backend API 호출 클라이언트.

모든 backend 통신은 이 모듈을 통해서만 수행한다.
직접 DB 접근이나 backend 내부 모듈 import 금지.
"""

import logging

import requests

from app.config import get_settings

logger = logging.getLogger(__name__)

# Backend URL (YAML 프로파일의 backend_url 설정에서 로딩, APP_PROFILE로 환경별 전환)
BASE_URL = get_settings().backend_url

# 기본 타임아웃 (초)
DEFAULT_TIMEOUT = 10

# 재시도 설정
MAX_RETRIES = 3
RETRY_INTERVAL = 2


def _request(
    method: str,
    path: str,
    *,
    params: dict | None = None,
    json: dict | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> requests.Response:
    """공통 HTTP 요청 함수 (재시도 포함)."""
    url = f"{BASE_URL}{path}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=timeout,
                proxies={"http": None, "https": None},
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt == MAX_RETRIES:
                raise
            import time

            time.sleep(RETRY_INTERVAL)

    # 도달하지 않음 (위에서 raise됨)
    raise requests.exceptions.RequestException("Max retries exceeded")


def get(path: str, params: dict | None = None) -> dict:
    """GET 요청."""
    response = _request("GET", path, params=params)
    return response.json()  # type: ignore[no-any-return]


def post(path: str, json: dict | None = None) -> dict:
    """POST 요청."""
    response = _request("POST", path, json=json)
    return response.json()  # type: ignore[no-any-return]


def put(path: str, json: dict | None = None) -> dict:
    """PUT 요청."""
    response = _request("PUT", path, json=json)
    return response.json()  # type: ignore[no-any-return]


def delete(path: str) -> dict:
    """DELETE 요청."""
    response = _request("DELETE", path)
    return response.json()  # type: ignore[no-any-return]


def health_check() -> bool:
    """Backend 서버 상태 확인."""
    try:
        result = get("/health")
        return result.get("status") == "hello atlas"
    except Exception:
        return False
