from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer
from voice_assistant.app_interfaces.i_command_recognizer import ICommandRecognizer


class CommandRecognizerSimple(ICommandRecognizer):
    def __init__(self):
        self._command_dict: dict[str, ICommandPerformer] = {}

    def add_command(self, command_class: ICommandPerformer):
        self._command_dict[command_class.get_command_topic()] = command_class
        pass

    async def process_command(self, command_text: str) -> str | None:
        for command_topic, command_performer in self._command_dict.items():
            if command_text != command_topic:
                continue
            break
        else:
            print(f"Не услышал команды: {command_text}")
            return

        command_res = await command_performer.perform_command(command_text)

        return command_res
