"""Frontend 설정 로더.

Backend와 동일한 YAML 프로파일(`config/application-{profile}.yml`)을 읽지만,
backend 내부 모듈(`app.config`)은 import하지 않는다.
(AGENTS.md: 프론트엔드에서 backend 내부 모듈 직접 import 금지)
"""

import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel


class FrontendSettings(BaseModel):
    """YAML 프로파일에서 로딩되는 프론트엔드 설정."""

    backend_url: str = "http://localhost:8000"


def load_config(profile: str | None = None) -> FrontendSettings:
    """YAML 프로파일 파일을 읽어 FrontendSettings 객체를 생성한다."""
    profile = profile or os.getenv("APP_PROFILE", "local")

    # 프로젝트 루트 기준 config 경로 탐색
    config_path = Path(__file__).parent.parent.parent / "config" / f"application-{profile}.yml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f) or {}

    # backend 전용 필드(db_*, api_host 등)는 FrontendSettings에 없으므로 무시된다.
    return FrontendSettings(**raw)


@lru_cache
def get_settings() -> FrontendSettings:
    """캐싱된 FrontendSettings 인스턴스를 반환한다. (앱 수명 동안 1회만 로딩)"""
    return load_config()
