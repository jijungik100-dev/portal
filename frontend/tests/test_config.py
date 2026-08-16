import pytest

from app.config import FrontendSettings, load_config


class TestLoadConfig:
    """load_config() 테스트."""

    def test_load_sample_profile(self) -> None:
        """sample 프로파일에서 backend_url을 정상적으로 읽는다."""
        settings = load_config(profile="sample")
        assert settings.backend_url == "http://localhost:8000"

    def test_load_missing_profile_raises(self) -> None:
        """존재하지 않는 프로파일은 FileNotFoundError를 발생시킨다."""
        with pytest.raises(FileNotFoundError):
            load_config(profile="does-not-exist")


def test_default_backend_url() -> None:
    """YAML에 backend_url이 없으면 기본값을 사용한다."""
    settings = FrontendSettings()
    assert settings.backend_url == "http://localhost:8000"
