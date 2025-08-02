from abc import ABC
from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)


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
