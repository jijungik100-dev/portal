import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel


class Settings(BaseModel):
    """YAML 프로파일에서 로딩되는 애플리케이션 설정."""

    env: str = "local"

    # Database
    db_type: str = "sqlite"
    db_host: str = ""
    db_port: int = 3306
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""
    db_path: str = "./local.db"

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_port: int = 8501

    @property
    def database_url(self) -> str:
        """프로파일에 따른 DB URL 생성."""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.db_path}"
        elif self.db_type == "mysql":
            return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")


def load_config(profile: str | None = None) -> Settings:
    """YAML 프로파일 파일을 읽어 Settings 객체를 생성한다."""
    profile = profile or os.getenv("APP_PROFILE", "local")

    # 프로젝트 루트 기준 config 경로 탐색
    config_path = Path(__file__).parent.parent.parent / "config" / f"application-{profile}.yml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f) or {}

    return Settings(**raw)


@lru_cache
def get_settings() -> Settings:
    """캐싱된 Settings 인스턴스를 반환한다. (앱 수명 동안 1회만 로딩)"""
    return load_config()
