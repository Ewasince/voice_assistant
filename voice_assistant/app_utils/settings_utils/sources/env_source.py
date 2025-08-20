from __future__ import annotations

from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import EnvSettingsSource


class ExtendedEnvSettingsSource(EnvSettingsSource):
    def prepare_field_value(self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool) -> Any:
        try:
            if field_name.lower().endswith("_list"):
                if not value:
                    return None
                return list(value.split(","))
            if field_name.lower().endswith("_map"):
                if not value:
                    return None
                result_map = {}
                for entry in value.split(";"):
                    key, value_ = entry.split(":")
                    result_map[key] = value_
                return result_map
            return super().prepare_field_value(field_name, field, value, value_is_complex)
        except Exception as e:
            raise ValueError(f"cant parse field {field_name}") from e
