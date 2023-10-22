from datetime import datetime

from app_interfaces.i_command_performer import ICommandPerformer


class CommandGetCurrentTime(ICommandPerformer):
    def get_command_topic(self) -> str:
        return "время"

    def perform_command(self, command_context: str) -> str | None:
        # extract_text_after_command(command_context, self.get_command_text())
        cur_time = datetime.now()
        return f"Сейчас время: {cur_time}"
