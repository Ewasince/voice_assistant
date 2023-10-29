import asyncio
from typing import NoReturn

from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer
from voice_assistant.app_interfaces.i_command_recognizer import ICommandRecognizer
from voice_assistant.app_interfaces.i_messages_recognizer import IMessagesRecognizer
from voice_assistant.app_interfaces.i_messages_source import IMessagesSource
from voice_assistant.command_recognizer.gpt import IGPTModule, YaGPTModule
from voice_assistant.command_recognizer.gpt.command_recognizer_gpt import CommandRecognizerGPT

###
from voice_assistant.commands.test_commands.command_get_current_os import (
    CommandGetCurrentOS,
)
from voice_assistant.commands.test_commands.command_get_current_time import (
    CommandGetCurrentTime,
)
from voice_assistant.massages_source.messages_source import MessagesSource
from voice_assistant.message_recognizer.local_mic.message_recognizer_local_mic import (
    MessageRecognizerLocalMic,
)


async def main() -> NoReturn:
    messages_recognizer: IMessagesRecognizer = MessageRecognizerLocalMic()
    message_source: IMessagesSource = MessagesSource(messages_recognizer)

    # command_recognizer: ICommandRecognizer = CommandRecognizerSimple()
    gpt_module: IGPTModule = YaGPTModule()
    # gpt_module: IGPTModule = GigaChatModule(input('> '))
    command_recognizer: ICommandRecognizer = CommandRecognizerGPT(gpt_module)

    ### commands

    command_time: ICommandPerformer = CommandGetCurrentOS()
    command_recognizer.add_command(command_time)

    command_time: ICommandPerformer = CommandGetCurrentTime()
    command_recognizer.add_command(command_time)

    ### main process

    while True:
        command = await message_source.wait_command()
        res = await command_recognizer.process_command(command)

        if res is not None:
            print(res)


command_source: IMessagesSource = ...

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Goodbye!")
