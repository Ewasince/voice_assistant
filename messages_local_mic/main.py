import os.path
import re
from typing import NoReturn

import pyaudio

from app_interfaces.i_messages_source import IMessagesSource
from messages_local_mic.audio import get_waw, AudioRecognizer
from messages_local_mic._command_performer import CommandPerformer
from messages_local_mic._commands import get_current_time, get_os_type
from messages_local_mic.config import config
from messages_local_mic.interfaces.i_command_performer import ICommandPerformer
from messages_local_mic.interfaces.i_messages_recognizer import IMessagesRecognizer
from messages_local_mic.utils import extract_text_after_command, normalize_text


class MessagesLocalMic(IMessagesSource):
    def __init__(self, recognizer: IMessagesRecognizer, performer: ICommandPerformer):
        self.recognizer = recognizer
        self.performer = performer
        return

    def _prepare_text(self, input_text: str) -> str | None:
        text = normalize_text(input_text)

        filtered_text = extract_text_after_command(text, config.key_phase)

        if filtered_text is None:
            # print(f'text not contain phase: {text}')
            return

        return filtered_text

    def _check_speech_after_word(
            self,
    ) -> str | None:
        text = self.recognizer.get_audio()
        if text is None:
            print("Ничего не услышал, слушаю дальше...")
            return

        filtered_text = self._prepare_text(text)
        if filtered_text is None:
            print(f"Не услышал команды: {text}")
            return

        return filtered_text

    def wait_command(self) -> str:
        while True:
            command = self._check_speech_after_word()
            if command is not None:
                break

        return command

    def _start_listen(
            self,
    ) -> NoReturn:
        """
        Дебаг метод

        :return:
        """
        self.performer.add_command("время", get_current_time)
        self.performer.add_command("система", get_os_type)

        while True:
            command = self.wait_command()

            self.performer.perform_command(command)

            pass
        pass


if __name__ == "__main__":
    try:
        messages_recognizer = AudioRecognizer()
        command_performer = CommandPerformer()

        messages_source = MessagesLocalMic(messages_recognizer, command_performer)

        messages_source._start_listen()
    except KeyboardInterrupt:
        print('Пока-пока...')
