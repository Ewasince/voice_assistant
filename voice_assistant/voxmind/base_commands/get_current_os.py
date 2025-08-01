import platform
from typing import Any, ClassVar

from voice_assistant.voxmind.app_interfaces.command_performer import CommandPerformer


class CommandGetCurrentOS(CommandPerformer):
    _command_topic: ClassVar[str] = "дать информацию о системе"

    async def perform_command(self, *args: Any) -> str | None:
        # os_type = os.name
        # match os_type:
        #     case "nt"
        #         os_name = "Windows"
        #     case ""
        # extract_text_after_command(command_text, self.get_command_text())
        os_name = platform.system()
        return f"Твоя система – {os_name}"
