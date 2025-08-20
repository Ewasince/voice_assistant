from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from voice_assistant.app_utils.settings_utils.helpers import find_yaml_path, load_yaml_cache


class YamlSettingsSource(PydanticBaseSettingsSource):
    """Источник верхнеуровневых настроек из YAML (для Settings)."""

    def __init__(self, settings_cls: type[BaseSettings], *, path: Path | None = None) -> None:
        super().__init__(settings_cls)
        self._path = path or find_yaml_path()
        self._data: dict[str, Any] = load_yaml_cache(self._path)

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

        if isinstance(self._data, dict) and key in self._data:
            return self._data[key], key, False

        # Ничего не нашли — следующий источник (ENV) получит шанс
        return None, key, False
