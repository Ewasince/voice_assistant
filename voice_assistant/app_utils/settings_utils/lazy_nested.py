from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel


class _LazyNested[T: BaseModel]:
    def __init__(
        self,
        model_cls: type[T],
        *yaml_keys: str,
        env_prefix_override: str | None = None,
        required: bool = True,
    ) -> None:
        self.model_cls = model_cls
        self.yaml_keys = [yaml_keys] if isinstance(yaml_keys, str) else yaml_keys
        self.env_prefix_override = env_prefix_override
        self.required = required
        self._name: str | None = None

    def __set_name__(self, owner: Any, name: str) -> None:
        self._name = name

    def __get__(self, obj: Any, objtype: Any = None) -> T:
        if obj is None:
            return self  # type: ignore[return-value]
        assert self._name is not None, "Descriptor name is not set"

        # Уже вычисляли?
        if self._name in obj.__dict__:
            return obj.__dict__[self._name]

        # 1) Достаём YAML секцию (если есть)
        yaml_data = obj._build_from_yaml_section(self.yaml_keys)

        # 2) Достаём ENV (по env_prefix из модели или override)
        env_data = obj._build_from_env(self.model_cls, self.env_prefix_override)

        # YAML → ENV (YAML приоритетнее, ENV дополняет недостающие поля):
        merged: dict[str, Any] = {**env_data, **yaml_data} if (yaml_data or env_data) else {}

        if not merged:
            if self.required:
                raise ValueError(
                    f"{self.model_cls.__name__}: не найдено значений ни в YAML секциях "
                    f"{self.yaml_keys!r}, ни в ENV (prefix "
                    f"{self.env_prefix_override or self._infer_prefix()!r})."
                )
            obj.__dict__[self._name] = None
            return obj.__dict__[self._name]

        instance = self.model_cls(**merged)
        obj.__dict__[self._name] = instance
        return instance

    def __set__(self, obj: Any, value: T | dict[str, Any]) -> None:
        assert self._name is not None, "Descriptor name is not set"
        if isinstance(value, self.model_cls):
            obj.__dict__[self._name] = value
        else:
            obj.__dict__[self._name] = self.model_cls(**value)  # type: ignore[arg-type]

    def _infer_prefix(self) -> str:
        cfg = getattr(self.model_cls, "model_config", {}) or {}
        if isinstance(cfg, dict):
            p = cfg.get("env_prefix")
            if p:
                return str(p)
        return ""


def lazy_nested[T: BaseModel](model_cls: type[T], *yaml_keys: str, **kwargs: Any) -> T:
    return cast(T, _LazyNested(model_cls, *yaml_keys, **kwargs))
