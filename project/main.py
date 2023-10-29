from typing import NoReturn

from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer
from voice_assistant.app_interfaces.i_command_recognizer import ICommandRecognizer
from voice_assistant.app_interfaces.i_messages_recognizer import IMessagesRecognizer
from voice_assistant.app_interfaces.i_messages_source import IMessagesSource
###
from voice_assistant.command_recognizer.simple.command_recognizer_simple import (
    CommandRecognizerSimple,
)
from voice_assistant.commands.command_get_current_os.command_get_current_os import (
    CommandGetCurrentOS,
)
from voice_assistant.commands.command_get_current_time.command_get_current_time import (
    CommandGetCurrentTime,
)
from voice_assistant.massages_source.messages_source import MessagesSourceLocalMic
from voice_assistant.message_recognizer.local_mic.message_recognizer_local_mic import (
    MessageRecognizerLocalMic,
)


def main() -> NoReturn:
    messages_recognizer: IMessagesRecognizer = MessageRecognizerLocalMic()
    message_source: IMessagesSource = MessagesSourceLocalMic(messages_recognizer)

    command_recognizer: ICommandRecognizer = CommandRecognizerSimple()

    ### commands

    command_time: ICommandPerformer = CommandGetCurrentOS()
    command_recognizer.add_command(command_time)

    command_time: ICommandPerformer = CommandGetCurrentTime()
    command_recognizer.add_command(command_time)

    ### main process

    while True:
        command = message_source.wait_command()
        res = command_recognizer.process_command(command)

        if res is not None:
            print(res)


command_source: IMessagesSource = ...

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Goodbye!")
