from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast, ClassVar

from pydantic import BaseModel, ConfigDict, PrivateAttr
from pydantic_core import PydanticUndefined
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, InitSettingsSource, \
    EnvSettingsSource, DotEnvSettingsSource, SecretsSettingsSource

from voice_assistant.app_utils.settings_utils.helpers import find_yaml_path, load_yaml_cache
from voice_assistant.app_utils.settings_utils.sources.env_source import ExtendedEnvSettingsSource
from voice_assistant.app_utils.settings_utils.sources.yaml_source import YamlSettingsSource


class ExtendedConfigDict(ConfigDict):
    env_prefix: str


class HierarchicalSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
    )

    # -------- внутренний кэш YAML --------
    _yaml_cache: dict[str, Any] = PrivateAttr()
    _init_only: bool = PrivateAttr()
    _data: dict[str, Any] = PrivateAttr()

    def __init__(
        self,
        yaml_path: str | None = None,
        yaml_cache: dict[str, Any] | None = None,
        init_only: bool = False,
        **values: Any,
    ):
        if not init_only and yaml_cache is None:
            yaml_path = (yaml_path and Path(yaml_path)) or find_yaml_path()
            yaml_cache = load_yaml_cache(yaml_path)

        yaml_cache = yaml_cache or {}

        self._yaml_cache = yaml_cache
        self._init_only = init_only
        self._data = values
        super().__init__(**values)

        # duplicate after pydantic initialization
        self._yaml_cache = yaml_cache
        self._init_only = init_only
        self._data = values


    # -------- настройка источников для верхних полей (YAML → ENV) --------
    def settings_customise_sources(
        self,
        settings_cls: type[BaseSettings],
        init_settings: InitSettingsSource,
        env_settings: EnvSettingsSource,  # noqa: ARG003
        dotenv_settings: DotEnvSettingsSource,  # noqa: ARG003
        file_secret_settings: SecretsSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Порядок: INIT → YAML → ENV → FILE_SECRETS

        if self._init_only:
            return (init_settings,)

        return (
            init_settings,
            YamlSettingsSource(settings_cls, self._yaml_cache),
            ExtendedEnvSettingsSource(settings_cls),
        )

    def get_yaml_section(self, section_keys: list[str]) -> dict[str, Any]:
        for key in section_keys:
            raw = self._yaml_cache.get(key)
            if isinstance(raw, dict):
                return raw
        return {}


class _LazyNested[T: HierarchicalSettings]:
    def __init__(
        self,
        model_cls: type[T],
        # *yaml_keys: str,
        # required: bool = True,
    ) -> None:
        self.model_cls = model_cls
        self._yaml_keys = []
        self._name: str | None = None

        self.required = True

    def __set_name__(self, owner: T, name: str) -> None:
        self._name = name
        self._yaml_keys.append(name)

    def __get__(self, obj: T, objtype: type[T] = None) -> T:
        if obj is None:
            return self  # type: ignore[return-value]
        assert self._name is not None, "Descriptor name is not set"

        # Уже вычисляли?
        if self._name in obj.__dict__:
            return obj.__dict__[self._name]

        # 1) Достаём YAML секцию (если есть)
        yaml_cache = obj.get_yaml_section(self._yaml_keys)

        instance = self.model_cls(
            yaml_cache=yaml_cache,
            init_only=obj._init_only,
            **obj._data.get(self._name, {}),
        )
        obj.__dict__[self._name] = instance
        return instance

    def __set__(self, obj: Any, value: T | dict[str, Any]) -> None:
        assert self._name is not None, "Descriptor name is not set"
        if isinstance(value, self.model_cls):
            obj.__dict__[self._name] = value
        else:
            obj.__dict__[self._name] = self.model_cls(**value)  # type: ignore[arg-type]


def lazy_nested[T: HierarchicalSettings](model_cls: type[T]) -> T:
    return cast(T, _LazyNested(model_cls))


if __name__ == '__main__':
    class InnerSettings(HierarchicalSettings):
        model_config = SettingsConfigDict(
            extra="ignore",
            env_prefix="INNER_"
        )
        test_var_3: int = 3
        test_var_4: int

    class Settings(HierarchicalSettings):
        test_var_1: int = 1
        test_var_2: int
        inner_settings: ClassVar[InnerSettings] = lazy_nested(InnerSettings)

    settings = Settings()
    print(settings.test_var_1)
    print(settings.test_var_2)

    inner = settings.inner_settings  # <--- error here !!!
    print(inner.test_var_3)
    print(inner.test_var_4)