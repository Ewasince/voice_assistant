from __future__ import annotations

from pathlib import Path
from typing import Any, Final, Iterable, Self, cast

from pydantic import PrivateAttr
from pydantic._internal._utils import deep_update
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    InitSettingsSource,
    PydanticBaseSettingsSource,
    SecretsSettingsSource,
    SettingsConfigDict,
)

from voice_assistant.app_utils.settings_utils.helpers import find_yaml_path, load_yaml_cache
from voice_assistant.app_utils.settings_utils.sources.env_source import ExtendedEnvSettingsSource
from voice_assistant.app_utils.settings_utils.sources.yaml_source import YamlSettingsSource

USERS_FIELD: Final[str] = "users"


class HierarchicalSettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
    )

    # -------- внутренний кэш YAML --------
    _yaml_cache: dict[str, Any] = PrivateAttr()
    _init_cache: dict[str, Any] = PrivateAttr()

    def __init__(
        self,
        yaml_path: str | None = None,
        yaml_cache: dict[str, Any] | None = None,
        **init_kwargs: Any,
    ):
        if yaml_cache is None:
            yaml_path_ = (yaml_path and Path(yaml_path)) or find_yaml_path()
            yaml_cache = load_yaml_cache(yaml_path_)

        yaml_cache = yaml_cache or {}

        self._yaml_cache = yaml_cache  # set for settings_customise_sources
        super().__init__(**init_kwargs)

        self._yaml_cache = yaml_cache
        self._init_cache = init_kwargs

    def settings_customise_sources(
        self,
        settings_cls: type[BaseSettings],
        init_settings: InitSettingsSource,  # type: ignore[override]
        env_settings: EnvSettingsSource,  # type: ignore[override]  # noqa: ARG002
        dotenv_settings: DotEnvSettingsSource,  # type: ignore[override]  # noqa: ARG002
        file_secret_settings: SecretsSettingsSource,  # type: ignore[override]  # noqa: ARG002
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Порядок: INIT → YAML → ENV → FILE_SECRETS

        return (
            init_settings,
            YamlSettingsSource(settings_cls, self._yaml_cache),
            ExtendedEnvSettingsSource(settings_cls),
        )

    def get_yaml_section(self, section_keys: Iterable[str]) -> dict[str, Any]:
        for key in section_keys:
            raw = self._yaml_cache.get(key)
            if isinstance(raw, dict):
                return raw
        return {}

    def merge(self, yaml_cache: dict[str, Any]) -> Self:
        yaml_cache = deep_update(self._yaml_cache, yaml_cache)
        cls = type(self)
        return cls(yaml_cache=yaml_cache)

    def get_nested_variables(self, *fields: str) -> dict[str, Any]:
        fields_dict = self._yaml_cache
        for field in fields:
            fields_dict = fields_dict.get(field, {})
        return fields_dict


class _LazyNested[T: HierarchicalSettings]:
    def __init__(
        self,
        model_cls: type[T],
    ) -> None:
        self.model_cls = model_cls
        self._yaml_keys: set[str] = set()
        self._name: str | None = None

        self.required = True

    def __set_name__(self, owner: T, field_name: str) -> None:
        self._yaml_keys.add(field_name)
        if field_name.endswith("_settings"):
            field_name = field_name[:-9]
        self._yaml_keys.add(field_name)
        self._name = field_name

    def __get__(self, obj: T, objtype: type[T] | None = None) -> T:
        if obj is None:
            return self
        assert self._name is not None, "Descriptor name is not set"

        if self._name in obj.__dict__:
            return obj.__dict__[self._name]

        yaml_cache = obj.get_yaml_section(self._yaml_keys)

        instance = self.model_cls(
            yaml_cache=yaml_cache,
            **obj._init_cache.get(self._name, {}),
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
