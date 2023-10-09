from typing import Callable

from messages_local_mic.interfaces.i_command_performer import ICommandPerformer
from messages_local_mic.utils import extract_text_after_command


class CommandPerformer(ICommandPerformer):
    def __init__(self):
        self._command_dict: dict[str, Callable[[str], None]] = {}
        return

    def add_command(self, command: str, callback: Callable[[], None]):
        self._command_dict[command] = callback
        return

    def delete_command(self, command: str):
        del self._command_dict[command]
        return

    def perform_command(self, text: str):
        for command, action in self._command_dict.items():
            if command not in text:
                continue
            filtered_text = extract_text_after_command(text, command)
            action(filtered_text)
            return

        return
