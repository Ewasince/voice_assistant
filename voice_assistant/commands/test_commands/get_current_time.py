from datetime import datetime
from typing import ClassVar

from voice_assistant.app_interfaces.command_performer import CommandPerformer


class CommandGetCurrentTime(CommandPerformer):
    _command_topic: ClassVar[str] = "время"

    async def perform_command(self, _: str) -> str | None:
        # extract_text_after_command(command_text, self.get_command_text())
        cur_time = datetime.now()  # noqa: DTZ005
        return f"Сейчас время: {cur_time}"
