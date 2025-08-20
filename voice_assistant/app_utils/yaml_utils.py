from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

# ... ваши импорты _find_yaml_path / _load_yaml_cache остаются


class YamlSettingsSource(PydanticBaseSettingsSource):
    """Источник верхнеуровневых настроек из YAML (для Settings)."""

    def __init__(self, settings_cls: type[BaseSettings], *, path: Path | None = None) -> None:
        super().__init__(settings_cls)
        self._path = path or _find_yaml_path()
        self._data: dict[str, Any] = _load_yaml_cache(self._path)

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


def _first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def _find_yaml_path() -> Path | None:
    """
    1) Явно через ENV: SETTINGS_YAML.
    2) Иначе ищем стандартные имена в CWD.
    """
    env_path = os.getenv("SETTINGS_YAML")
    if env_path:
        p = Path(env_path).expanduser()
        return p if p.exists() else None

    candidates = [
        Path("settings.yaml"),
        Path("settings.yml"),
        Path("config.yaml"),
        Path("config.yml"),
    ]
    return _first_existing(candidates)


def _load_yaml_cache(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except FileNotFoundError:
        return {}
    except Exception:
        # без лишней драматизации: если yaml сломан — игнорим, но не валим приложение
        return {}
