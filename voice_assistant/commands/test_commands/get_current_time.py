from datetime import datetime

from voice_assistant.app_interfaces.command_performer import ICommandPerformer


class CommandGetCurrentTime(ICommandPerformer):
    def get_command_topic(self) -> str:
        return "время"

    async def perform_command(self, command_context: str) -> str | None:
        # extract_text_after_command(command_context, self.get_command_text())
        cur_time = datetime.now()
        return f"Сейчас время: {cur_time}"
