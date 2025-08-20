from __future__ import annotations

from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import EnvSettingsSource


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
