from __future__ import annotations

from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource


class YamlSettingsSource(PydanticBaseSettingsSource):
    def __init__(
        self,
        settings_cls: type[BaseSettings],
        yaml_cache: dict[str, Any],
    ):
        super().__init__(settings_cls)
        self._yaml_cache = yaml_cache

    # Абстрактный метод — должен вернуть уже собранный dict для парсинга Settings
    def __call__(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        # Берём только известные поля Settings, учитывая alias
        for field_name, field in self.settings_cls.model_fields.items():
            v, _key, _complex = self.get_field_value(field, field_name)
            if v is not None:
                values[field_name] = v
        return values

    # Абстрактный метод — как доставать значение для конкретного поля
    def get_field_value(
        self,
        field: FieldInfo,
        field_name: str,
    ) -> tuple[Any, str, bool]:
        """
        Возвращает (value, key, is_complex).
        - value: значение из YAML или None
        - key:   фактический ключ, по которому искали (alias > field_name)
        - is_complex: False — YAML уже даёт готовые Python-значения
        """
        key = field.alias or field_name

        # Ничего не нашли — следующий источник (ENV) получит шанс
        return self._yaml_cache.get(key), key, False
