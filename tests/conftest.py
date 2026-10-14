import pytest

from app.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(postgres_password="test", _env_file=None)
