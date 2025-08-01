from dataclasses import dataclass, field
from typing import Any


@dataclass
class Context:
    command_history: list = field(default_factory=list)
    command_notes: dict[str, Any] = field(default_factory=dict)
