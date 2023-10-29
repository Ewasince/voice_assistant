from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer
from voice_assistant.app_interfaces.i_command_recognizer import ICommandRecognizer


class CommandRecognizerSimple(ICommandRecognizer):

    async def process_command_from_dict(self, command_text: str) -> str | None:
        for command_topic, command_performer in self._command_dict.items():
            if not command_text.startswith(command_topic):
                continue
            break
        else:
            print(f"Не услышал команды: {command_text}")
            return

        command_text = command_text[len(command_topic):].strip()
        command_res = await command_performer.perform_command(command_text)

        return command_res
