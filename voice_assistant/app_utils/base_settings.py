from __future__ import annotations

import os
from abc import ABC
from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, PrivateAttr
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from voice_assistant.app_utils.yaml_utils import YamlSettingsSource, _find_yaml_path, _load_yaml_cache


class ExtendedSource(EnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        try:
            if field_name.lower().endswith("_list"):
                return list(value.split(","))
            if field_name.lower().endswith("_map"):
                result_map = {}
                for entry in value.split(";"):
                    key, value = entry.split(":")
                    result_map[key] = value
                return result_map
            return super().prepare_field_value(field_name, field, value, value_is_complex)
        except Exception as e:
            raise ValueError from e


class ExtendedSettings(BaseSettings, ABC):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (ExtendedSource(settings_cls),)


class _LazyNested[T: BaseModel]:
    def __init__(
        self,
        model_cls: type[T],
        *yaml_keys: str,
        env_prefix_override: str | None = None,
        required: bool = True,
    ) -> None:
        self.model_cls = model_cls
        self.yaml_keys = [yaml_keys] if isinstance(yaml_keys, str) else yaml_keys
        self.env_prefix_override = env_prefix_override
        self.required = required
        self._name: str | None = None

    def __set_name__(self, owner: Any, name: str) -> None:
        self._name = name

    def __get__(self, obj: Any, objtype: Any = None) -> T:
        if obj is None:
            return self  # type: ignore[return-value]
        assert self._name is not None, "Descriptor name is not set"

        # Уже вычисляли?
        if self._name in obj.__dict__:
            return obj.__dict__[self._name]

        # 1) Достаём YAML секцию (если есть)
        yaml_data = obj._build_from_yaml_section(self.yaml_keys)

        # 2) Достаём ENV (по env_prefix из модели или override)
        env_data = obj._build_from_env(self.model_cls, self.env_prefix_override)

        # YAML → ENV (YAML приоритетнее, ENV дополняет недостающие поля):
        merged: dict[str, Any] = {**env_data, **yaml_data} if (yaml_data or env_data) else {}

        if not merged:
            if self.required:
                raise ValueError(
                    f"{self.model_cls.__name__}: не найдено значений ни в YAML секциях "
                    f"{self.yaml_keys!r}, ни в ENV (prefix "
                    f"{self.env_prefix_override or self._infer_prefix()!r})."
                )
            obj.__dict__[self._name] = None
            return obj.__dict__[self._name]

        instance = self.model_cls(**merged)
        obj.__dict__[self._name] = instance
        return instance

    def __set__(self, obj: Any, value: T | dict[str, Any]) -> None:
        assert self._name is not None, "Descriptor name is not set"
        if isinstance(value, self.model_cls):
            obj.__dict__[self._name] = value
        else:
            obj.__dict__[self._name] = self.model_cls(**value)  # type: ignore[arg-type]

    def _infer_prefix(self) -> str:
        cfg = getattr(self.model_cls, "model_config", {}) or {}
        if isinstance(cfg, dict):
            p = cfg.get("env_prefix")
            if p:
                return str(p)
        return ""


def lazy_nested[T: BaseModel](model_cls: type[T], *yaml_keys: str, **kwargs: Any) -> T:
    # Возвращаем LazyNested, но типизатору говорим, что это T
    return cast(T, _LazyNested(model_cls, *yaml_keys, **kwargs))


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
        self._yaml_path = (yaml_path and Path(yaml_path)) or _find_yaml_path()
        self._yaml_cache = _load_yaml_cache(self._yaml_path)

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
