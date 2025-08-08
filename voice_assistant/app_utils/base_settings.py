from abc import ABC
from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)


class _LazySettings[T]:
    def __init__(self, cls: type[T]):
        print("__init__ lazy")
        self._cls = cls

    _obj: T | None = None

    def __getattr__(self, item: str) -> Any:
        print(f"get attr from lazy {item}")
        # avoid pyCharm debugger
        if item == "shape":
            return None
        return getattr(self._get(), item)

    def _get(self) -> T:
        if self._obj is None:
            # noinspection PyArgumentList
            print("init from lazy!")
            self._obj = self._cls()
        return self._obj


def lazy[T](cls: type[T]) -> T:
    return _LazySettings[T](cls)  # type: ignore[return-value]


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
