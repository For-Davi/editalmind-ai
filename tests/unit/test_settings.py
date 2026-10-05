import pytest
from pydantic import ValidationError

from editalmind_ai.infrastructure.settings import Settings, get_settings


def test_defaults_target_local_environment() -> None:
    settings = Settings(_env_file=None)

    assert settings.environment == "local"
    assert settings.debug is False
    assert settings.docs_enabled is True


def test_reads_prefixed_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_ENVIRONMENT", "staging")
    monkeypatch.setenv("AI_DEBUG", "true")

    settings = Settings(_env_file=None)

    assert settings.environment == "staging"
    assert settings.debug is True


def test_rejects_unknown_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_ENVIRONMENT", "qa")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_docs_are_disabled_in_production() -> None:
    assert Settings(_env_file=None, environment="production").docs_enabled is False


def test_settings_are_immutable() -> None:
    settings = Settings(_env_file=None)

    with pytest.raises(ValidationError):
        settings.environment = "production"  # type: ignore[misc]


def test_get_settings_returns_cached_instance() -> None:
    get_settings.cache_clear()

    assert get_settings() is get_settings()
