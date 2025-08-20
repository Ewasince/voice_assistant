from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


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
        Path(p) / name
        for p in (
            "",
            "data",
        )
        for name in (
            "settings.yaml",
            "settings.yml",
            "config.yaml",
            "config.yml",
        )
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
