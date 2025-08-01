from dataclasses import dataclass
from datetime import datetime


@dataclass
class Contex:
    last_activity_topic: str | None = None
    last_activity_time: datetime | None = None
