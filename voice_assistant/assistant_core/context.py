from dataclasses import dataclass, field


@dataclass
class Context:
    command_history: list = field(default_factory=list)
    command_notes: dict = field(default_factory=dict)
