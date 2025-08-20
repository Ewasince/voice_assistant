from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, PrivateAttr
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from voice_assistant.app_utils.settings_utils.helpers import find_yaml_path, load_yaml_cache
from voice_assistant.app_utils.settings_utils.sources.env_source import ExtendedSource
from voice_assistant.app_utils.settings_utils.sources.yaml_source import YamlSettingsSource


class ExtendedConfigDict(ConfigDict):
    env_prefix: str


class HierarchicalSettings(BaseSettings):
    """
    Верхнеуровневые поля читаются при инициализации (приоритет YAML → ENV).
    Вложенные поля, помеченные _LazyNested, инициализируются лениво при первом доступе
    с приоритетом YAML → ENV (YAML значения перекрывают ENV, а ENV дополняет недостающие).
    """

    model_config = SettingsConfigDict(
        extra="ignore",
    )

    # -------- внутренний кэш YAML --------
    _yaml_path: Path | None = PrivateAttr(default=None)
    _yaml_cache: dict[str, Any] = PrivateAttr(default_factory=dict)

    # -------- настройка источников для верхних полей (YAML → ENV) --------
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Порядок: INIT → YAML → ENV → FILE_SECRETS

        return (
            init_settings,
            # settings_cls,  # YAML приоритетнее ENV
            YamlSettingsSource(settings_cls),  # YAML приоритетнее ENV
            ExtendedSource(settings_cls),
            # env_settings,
            file_secret_settings,
        )

    # -------- lifecycle --------
    def __init__(self, yaml_path: str | None = None, yaml_cache: dict[str, Any] | None = None, **values: Any):
        super().__init__(**values)
        if yaml_cache:
            self._yaml_cache = yaml_cache
            return
        self._yaml_path = (yaml_path and Path(yaml_path)) or find_yaml_path()
        self._yaml_cache = load_yaml_cache(self._yaml_path)

    # -------- helpers для дескрипторов --------
    def _build_from_env(
        self,
        model_cls: type[BaseModel],
        prefix_override: str | None = None,
    ) -> dict[str, Any]:
        """
        Собираем dict из ENV по именам полей модели:
        поле `api_key` + prefix `COMPOSIO_` → `COMPOSIO_API_KEY`, и т.д.
        """
        # Определяем префикс
        prefix = prefix_override or ""
        cfg = getattr(model_cls, "model_config", {}) or {}
        if not prefix and isinstance(cfg, dict):
            prefix = str(cfg.get("env_prefix") or "")
        # Собираем значения
        result: dict[str, Any] = {}
        for name in model_cls.model_fields:
            env_name = (prefix + name).upper().replace(".", "_")
            if env_name in os.environ:
                result[name] = os.environ[env_name]
        return result

    def _build_from_yaml_section(self, section_keys: list[str]) -> dict[str, Any]:
        for key in section_keys:
            raw = self._yaml_cache.get(key)
            if isinstance(raw, dict):
                return raw
        return {}
