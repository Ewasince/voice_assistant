from datetime import datetime
from typing import Any, ClassVar

from voice_assistant.app_interfaces.command_performer import CommandPerformer


class CommandGetCurrentTime(CommandPerformer):
    _command_topic: ClassVar[str] = "время"

    async def perform_command(self, *args: Any) -> str | None:
        # extract_text_after_command(command_text, self.get_command_text())
        cur_time = datetime.now()  # noqa: DTZ005
        return f"Сейчас время: {cur_time}"
