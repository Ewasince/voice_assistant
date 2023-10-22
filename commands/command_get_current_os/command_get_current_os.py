import platform

from app_interfaces.i_command_performer import ICommandPerformer


class CommandGetCurrentOS(ICommandPerformer):
    def get_command_topic(self) -> str:
        return "система"

    def perform_command(self, command_context: str) -> str | None:
        # os_type = os.name
        # match os_type:
        #     case "nt"
        #         os_name = "Windows"
        #     case ""
        # extract_text_after_command(command_context, self.get_command_text())
        os_name = platform.system()
        return f"Твоя система – {os_name}"
