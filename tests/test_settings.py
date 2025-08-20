# pytest unit tests for HierarchicalSettings / YamlSettingsSource / lazy_nested
# NOTE: Adjust the import path below to your module location.
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, ClassVar

import pytest
import yaml
from pydantic import ValidationError, SecretStr, BaseModel
from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import ExtendedConfigDict, HierarchicalSettings, lazy_nested


class AgentSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
    )
    model: str = "openai/gpt-4.1-mini"
    api_key: SecretStr

class Settings(HierarchicalSettings):
    debug_mode: bool = False
    database_uri: str

    agent_settings: ClassVar[AgentSettings] = lazy_nested(AgentSettings)



# ------------------------------
# Helpers & fixtures
# ------------------------------
@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch):
    """Isolate environment between tests."""
    keys = [
        *(k for k in list(os.environ.keys()) if k.startswith("AGENT_")),
        "DATABASE_URI",
        "DEBUG_MODE",
        "SETTINGS_YAML",
        "AGENT_MODEL",
        "AGENT_API_KEY",
    ]
    for k in keys:
        monkeypatch.delenv(k, raising=False)


@pytest.fixture()
def write_yaml(tmp_path: Path) -> Callable[[dict[str, Any], str], Path]:
    def _write(data: dict[str, Any], name: str = "settings.yaml") -> Path:
        p = tmp_path / name
        with p.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True)
        return p

    return _write


# Factory to create Settings with optional yaml_path/cache
@pytest.fixture()
def make_settings() -> Callable[..., Settings]:
    def _make(
        yaml_path: str | None = None,
        data: dict[str, Any] | None = None,
        paticular: bool = False,  # NEW
        **kwargs: Any,
    ) -> Settings:
        # noinspection PyArgumentList
        return Settings(
            yaml_path=yaml_path,
            data=data,
            paticular=paticular,
            **kwargs,
        )

    return _make


# ------------------------------
# 1) Источники верхнего уровня: YAML → ENV
# ------------------------------

def test_01_yaml_overrides_env_debug_mode(write_yaml, make_settings, monkeypatch):
    # YAML: debug_mode: true, ENV: DEBUG_MODE=false -> YAML wins
    p = write_yaml({"debug_mode": True})
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")  # required field
    monkeypatch.setenv("DEBUG_MODE", "false")

    s = make_settings(yaml_path=str(p))
    assert s.debug_mode is True


def test_02_env_used_when_yaml_missing_key(write_yaml, make_settings, monkeypatch):
    # YAML without database_uri, ENV provides it
    p = write_yaml({"debug_mode": False})
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")

    s = make_settings(yaml_path=str(p))
    assert s.database_uri == "postgres://env/db"


def test_03_no_yaml_file_env_only(make_settings, monkeypatch):
    # No YAML path, rely on ENV only
    monkeypatch.setenv("DATABASE_URI", "postgres://env/only")
    s = make_settings()
    assert s.database_uri == "postgres://env/only"


def test_04_broken_yaml_falls_back_to_env(tmp_path, make_settings, monkeypatch):
    p = tmp_path / "settings.yaml"
    p.write_text("debug_mode: [unclosed", encoding="utf-8")
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")

    s = make_settings(yaml_path=str(p))
    assert s.database_uri == "postgres://env/db"


def test_05_yaml_extra_keys_ignored(write_yaml, make_settings, monkeypatch):
    p = write_yaml({"debug_mode": True, "unknown_key": 123, "database_uri": "postgres://yaml/db"})
    s = make_settings(yaml_path=str(p))
    assert s.database_uri == "postgres://yaml/db"
    assert s.debug_mode is True


# ------------------------------
# 2) data / yaml_path behavior
# ------------------------------

def test_06_yaml_cache_disables_env_upper_level(make_settings, monkeypatch):
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")
    s = make_settings(data={"database_uri": "postgres://cache/db"})
    assert s.database_uri == "postgres://cache/db"


def test_07_yaml_path_normal_priority(write_yaml, make_settings, monkeypatch):
    p = write_yaml({"database_uri": "postgres://yaml/db", "debug_mode": True})
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")

    s = make_settings(yaml_path=str(p))
    assert s.database_uri == "postgres://yaml/db"
    assert s.debug_mode is True


def test_08_yaml_cache_empty_env_ignored_and_error_on_required(make_settings, monkeypatch):
    # data={} disables ENV, required database_uri missing -> ValidationError
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")
    with pytest.raises(ValidationError):
        make_settings(data={})


# ------------------------------
# 3) Ленивая инициализация nested (AgentSettings)
# ------------------------------

def test_09_lazy_no_access_no_error(make_settings, monkeypatch):
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")
    s = make_settings()
    # No access to s.agent_settings here -> should not raise
    assert s.database_uri == "postgres://env/db"


def test_10_first_access_yaml_then_fill_from_env(write_yaml, make_settings, monkeypatch):
    # YAML provides model; ENV provides missing api_key
    p = write_yaml({
        "database_uri": "postgres://yaml/db",
        "agent_settings": {"model": "mistral"},
    })
    monkeypatch.setenv("AGENT_API_KEY", "sk_env")

    s = make_settings(yaml_path=str(p))
    a = s.agent_settings
    assert a.model == "mistral"
    assert a.api_key.get_secret_value() == "sk_env"


def test_11_multiple_yaml_keys_prefer_first(write_yaml, make_settings, monkeypatch):
    p = write_yaml({
        "database_uri": "postgres://yaml/db",
        "agent_settings": {"model": "first"},
        "agent": {"model": "second"},
    })
    monkeypatch.setenv("AGENT_API_KEY", "sk_env")

    s = make_settings(yaml_path=str(p))
    assert s.agent_settings.model == "first"


def test_12_nested_cached_id_stable(write_yaml, make_settings, monkeypatch):
    p = write_yaml({
        "database_uri": "postgres://yaml/db",
        "agent_settings": {"model": "x"},
    })
    monkeypatch.setenv("AGENT_API_KEY", "sk_env")

    s = make_settings(yaml_path=str(p))
    a1 = s.agent_settings
    a2 = s.agent_settings
    assert id(a1) == id(a2)


# ------------------------------
# 4) data disables ENV for nested as well
# ------------------------------

def test_13_yaml_cache_disables_env_for_nested(make_settings, monkeypatch):
    s = make_settings(
        data={
            "database_uri": "postgres://cache/db",
            "agent_settings": {"api_key": "sk_yaml"},
        }
    )
    monkeypatch.setenv("AGENT_API_KEY", "sk_env")

    a = s.agent_settings
    assert a.api_key.get_secret_value() == "sk_yaml"


# ------------------------------
# 5) paticular=True (частичная сборка)
# ------------------------------

def test_14_paticular_top_level_skips_required_validation(make_settings):
    # With paticular=True and empty data, constructor should not fail
    s = make_settings(data={}, paticular=True)
    # database_uri is missing but instance exists
    assert isinstance(s, Settings)


def test_15_paticular_nested_empty_constructs(write_yaml, make_settings, monkeypatch):
    p = write_yaml({"database_uri": "postgres://yaml/db"})
    s = make_settings(yaml_path=str(p), paticular=True)
    a = s.agent_settings
    dumped = a.model_dump(exclude_unset=True)
    assert "api_key" not in dumped
    assert a.model == "openai/gpt-4.1-mini"


def test_16_paticular_nested_partial_yaml(write_yaml, make_settings):
    p = write_yaml({
        "database_uri": "postgres://yaml/db",
        "agent_settings": {"model": "custom"},
    })
    s = make_settings(yaml_path=str(p), paticular=True)
    dumped = s.agent_settings.model_dump(exclude_unset=True)
    assert dumped.get("model") == "custom"
    assert "api_key" not in dumped


# ------------------------------
# 6) Обычный режим (paticular=False)
# ------------------------------

def test_17_nested_absent_raises_on_access(make_settings, monkeypatch):
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")
    s = make_settings()
    with pytest.raises(ValueError):
        _ = s.agent_settings


def test_18_nested_yaml_missing_required_raises(write_yaml, make_settings):
    p = write_yaml({
        "database_uri": "postgres://yaml/db",
        "agent_settings": {"model": "only"},
    })
    s = make_settings(yaml_path=str(p))
    with pytest.raises(ValidationError):
        _ = s.agent_settings


# ------------------------------
# 7) Аннотации и невключение nested в поля модели
# ------------------------------

def test_19_agent_settings_not_in_model_fields():
    assert "agent_settings" not in Settings.model_fields


# ------------------------------
# 8) Merge конфигов (часть 1)
# ------------------------------

def test_20_merge_upper_fields(write_yaml, make_settings, monkeypatch):
    # base
    p_base = write_yaml({"database_uri": "postgres://base/db", "debug_mode": False})
    base = make_settings(yaml_path=str(p_base))

    # user overrides debug_mode via data
    user = make_settings(data={"debug_mode": True})

    merged = base.merge(user)
    assert isinstance(merged, Settings)
    assert merged is not base and merged is not user
    assert merged.database_uri == "postgres://base/db"
    assert merged.debug_mode is True

# ------------------------------
# 21) Merge nested: base not initialized, user initialized (overlay on first access)
# ------------------------------

def test_21_merge_nested_base_lazy_user_initialized_overlay_first_access(write_yaml, make_settings, monkeypatch):
    # base: has sources for agent (model in YAML, key in ENV) but NOT initialized
    p_base = write_yaml({
        "database_uri": "postgres://base/db",
        "agent_settings": {"model": "base_model"},
    })
    monkeypatch.setenv("AGENT_API_KEY", "base_key")
    base = make_settings(yaml_path=str(p_base))

    # user: initialized nested with only model override
    p_user = write_yaml({
        "database_uri": "postgres://user/db",
        "agent_settings": {"model": "user_model"},
    })
    user = make_settings(yaml_path=str(p_user))
    # Force initialization of user's nested
    _ = user.agent_settings

    merged = base.merge(user)

    # On first access, merged should build from base sources and overlay user values
    a = merged.agent_settings
    assert a.model == "user_model"          # overridden by user
    assert a.api_key.get_secret_value() == "base_key"  # kept from base


# ------------------------------
# 22) Merge nested: both initialized (same overlay principle)
# ------------------------------

def test_22_merge_nested_both_initialized_overlay(write_yaml, make_settings, monkeypatch):
    # base initialized with model only
    p_base = write_yaml({
        "database_uri": "postgres://base/db",
        "agent_settings": {"model": "a"},
    })
    monkeypatch.setenv("AGENT_API_KEY", "base_key")
    base = make_settings(yaml_path=str(p_base))
    _ = base.agent_settings

    # user initialized with api_key only (as SecretStr via ENV or YAML)
    p_user = write_yaml({
        "database_uri": "postgres://user/db",
        "agent_settings": {},
    })
    monkeypatch.setenv("AGENT_API_KEY", "user_key")
    user = make_settings(yaml_path=str(p_user))
    # Ensure USER nested init reflects user_key
    _ = user.agent_settings

    merged = base.merge(user)
    a = merged.agent_settings
    assert a.model == "a"                      # from base
    assert a.api_key.get_secret_value() == "user_key"  # overridden by user


# ------------------------------
# 23) Merge: modes/sources inherited from base
# ------------------------------

def test_23_merge_inherits_modes_and_sources(write_yaml, make_settings, monkeypatch):
    # base has data (=> ENV disabled) and paticular=True
    base = make_settings(data={"database_uri": "postgres://cache/db"}, paticular=True)

    # user tries to override via ENV and yaml_path
    p_user = write_yaml({"database_uri": "postgres://user/db"})
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")
    user = make_settings(yaml_path=str(p_user))

    merged = base.merge(user)

    # ENV should remain disabled (value from cache must stay)
    assert merged.database_uri == "postgres://cache/db"

    # paticular=True should allow lazy nested to construct without required fields
    # No agent info anywhere -> access should not raise
    a = merged.agent_settings
    dumped = a.model_dump(exclude_unset=True)
    assert "api_key" not in dumped


# ------------------------------
# 24) Immutability after merge
# ------------------------------

def test_24_merge_immutability(write_yaml, make_settings, monkeypatch):
    p_base = write_yaml({
        "database_uri": "postgres://base/db",
        "agent_settings": {"model": "base_model"},
    })
    monkeypatch.setenv("AGENT_API_KEY", "base_key")
    base = make_settings(yaml_path=str(p_base))

    p_user = write_yaml({
        "database_uri": "postgres://user/db",
        "agent_settings": {"model": "user_model"},
    })
    user = make_settings(yaml_path=str(p_user))
    _ = user.agent_settings

    merged = base.merge(user)
    # mutate base and user after merge
    base.debug_mode = True
    _ = user.agent_settings  # already initialized
    user.agent_settings.model = "user_model2"

    a = merged.agent_settings
    assert a.model == "user_model"  # unaffected by later changes
    assert merged.debug_mode is False


# ------------------------------
# 25) SecretStr overwriting
# ------------------------------

def test_25_secretstr_overwrites(write_yaml, make_settings, monkeypatch):
    p_base = write_yaml({
        "database_uri": "postgres://base/db",
        "agent_settings": {"model": "m"},
    })
    monkeypatch.setenv("AGENT_API_KEY", "base_key")
    base = make_settings(yaml_path=str(p_base))
    _ = base.agent_settings

    # user provides new secret in YAML
    p_user = write_yaml({
        "database_uri": "postgres://user/db",
        "agent_settings": {"api_key": "user_key"},
    })
    user = make_settings(yaml_path=str(p_user))
    _ = user.agent_settings

    merged = base.merge(user)
    assert merged.agent_settings.api_key.get_secret_value() == "user_key"


# ------------------------------
# 26) env_prefix model (AGENT_) without YAML
# ------------------------------

def test_26_env_prefix_model(make_settings, monkeypatch):
    monkeypatch.setenv("DATABASE_URI", "postgres://env/db")
    monkeypatch.setenv("AGENT_API_KEY", "sk")
    s = make_settings()
    assert s.agent_settings.api_key.get_secret_value() == "sk"


# ------------------------------
# 27) env_prefix_override (custom descriptor in test)
# ------------------------------

def test_27_env_prefix_override(write_yaml, monkeypatch):
    class TestAgent(AgentSettings):
        pass

    class TestSettings(HierarchicalSettings):
        debug_mode: bool = False
        database_uri: str
        # Override prefix to MYAGENT_
        agent_settings: ClassVar[TestAgent] = lazy_nested(TestAgent, "agent_settings", env_prefix_override="MYAGENT_")

    p = write_yaml({"database_uri": "postgres://yaml/db"})
    monkeypatch.setenv("MYAGENT_AGENT_API_KEY", "sk2")

    s = TestSettings(yaml_path=str(p))
    assert s.agent_settings.api_key.get_secret_value() == "sk2"


# ------------------------------
# 28) Multi YAML keys order preserved
# ------------------------------

def test_28_multi_yaml_keys_order(write_yaml, make_settings, monkeypatch):
    p = write_yaml({
        "database_uri": "postgres://yaml/db",
        "agent_settings": {"model": "first"},
        "agent": {"model": "second"},
    })
    monkeypatch.setenv("AGENT_API_KEY", "sk_env")
    s = make_settings(yaml_path=str(p))
    assert s.agent_settings.model == "first"


# ------------------------------
# 29) Setter from dict
# ------------------------------

def test_29_setter_from_dict(write_yaml, make_settings):
    p = write_yaml({"database_uri": "postgres://yaml/db"})
    s = make_settings(yaml_path=str(p), paticular=True)
    s.agent_settings = {"model": "x", "api_key": "sk"}
    assert s.agent_settings.model == "x"
    assert s.agent_settings.api_key.get_secret_value() == "sk"


# ------------------------------
# 30) Setter from instance
# ------------------------------

def test_30_setter_from_instance(write_yaml, make_settings):
    p = write_yaml({"database_uri": "postgres://yaml/db"})
    s = make_settings(yaml_path=str(p))
    inst = AgentSettings(api_key=SecretStr("sk"))
    s.agent_settings = inst
    assert s.agent_settings is inst


# ------------------------------
# 31) Required fields rules
# ------------------------------

def test_31_required_fields_rules(make_settings, write_yaml, monkeypatch):
    # Settings has required database_uri -> error when missing if paticular=False
    with pytest.raises(ValidationError):
        _ = make_settings()

    # AgentSettings required api_key should NOT raise on Settings construction
    p = write_yaml({"database_uri": "postgres://yaml/db"})
    s = make_settings(yaml_path=str(p))
    # error occurs only when accessing nested in normal mode
    with pytest.raises((ValidationError, ValueError)):
        _ = s.agent_settings


# ------------------------------
# 32) Big YAML smoke test
# ------------------------------

def test_32_big_yaml_smoke(write_yaml, make_settings, monkeypatch):
    big: dict[str, Any] = {"database_uri": "postgres://big/db"}
    # add many unrelated keys
    for i in range(1000):
        big[f"unused_{i}"] = i
    p = write_yaml(big)
    s = make_settings(yaml_path=str(p))
    assert s.database_uri == "postgres://big/db"
