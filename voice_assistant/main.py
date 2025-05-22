import asyncio
import sys
from typing import NoReturn

from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger
from uvicorn import Config, Server

from voice_assistant.utils.settings import VASettings
from voxmind.app_interfaces.command_source import CommandSource
from voxmind.app_utils.settings import Settings

logger.remove()  # Удаляем стандартный вывод в stderr
logger.add(sys.stdout, level="DEBUG")  # Добавляем вывод в stdout


async def main() -> NoReturn:

    load_dotenv()
    settings = VASettings()

    # create llm module
    from voxmind.app_interfaces.llm_module import LLMClient
    from voxmind.llm_clients.gigachat_client import GigaChatClient

    gpt_module: LLMClient = GigaChatClient(settings)

    # topic definer, which determines which command need to activate
    from voxmind.app_interfaces.topic_definer import TopicDefiner
    from voxmind.topic_definers.llm_based import TopicDefinerGPT

    topic_definer: TopicDefiner = TopicDefinerGPT(gpt_module)

    # create command recognizer, which recognize command by using topic definer
    from voxmind.assistant_core.command_recognizer import CommandRecognizer

    command_recognizer: CommandRecognizer = CommandRecognizer(topic_definer)

    ### commands
    from voxmind.app_interfaces.command_performer import CommandPerformer

    # так же добавляем команды. Каждая команда – это класс, который должен реализовывать интерфейс команды
    from voxmind.base_commands.get_current_os import CommandGetCurrentOS

    command_os: CommandPerformer = CommandGetCurrentOS()
    command_recognizer.add_command(command_os.command_topic, command_os)

    from voxmind.base_commands.get_current_time import CommandGetCurrentTime

    command_time: CommandPerformer = CommandGetCurrentTime()
    command_recognizer.add_command(command_time.command_topic, command_time)

    from voice_assistant.commands.time_keeper import CommandTimeKeeperGoogle

    command_tk: CommandPerformer = CommandTimeKeeperGoogle(gpt_module)
    command_recognizer.add_command(command_tk.command_topic, command_tk)

    # command_notion: ICommandPerformer = CommandGPTNotion(llm_client, topic_definer)
    # command_recognizer.add_command(command_notion)

    from voxmind.base_commands.llm_question import CommandLLMQuestion

    command_default: CommandPerformer = CommandLLMQuestion(gpt_module)
    command_recognizer.add_command(None, command_default)

    ### main process
    # и, например, в цикле получаем от источника команд текстовые сообщения и обрабатываем их

    # create commands source iterator

    command_source = get_local_source(settings)

    command_text: str
    async for command_text in command_source:
        command_result = await command_recognizer.process_command_from_text(command_text)
        assistant_response = f"Ответ ассистента > {command_result}"

        if command_result is not None:
            print(assistant_response)
        else:
            print()
    sys.exit(1)  # Завершение программы с кодом ошибки

def get_local_source(settings: Settings) -> CommandSource:
    from voxmind.commands_sources.local_voice_command_source.command_source import LocalVoiceCommandSource

    command_source: CommandSource = LocalVoiceCommandSource(settings)
    return command_source

def get_web_source(settings: Settings) -> CommandSource:
    from voxmind.commands_sources.web_voice_command_source.command_source import WebVoiceCommandSource
    app = FastAPI()
    command_source: CommandSource = WebVoiceCommandSource(settings, app)

    config = Config(app=app, host="127.0.0.1", port=8010, loop="asyncio")
    server = Server(config)

    asyncio.create_task(server.serve())  # noqa: RUF006
    logger.info("Web api created")
    return command_source


if __name__ == "__main__":
    # noinspection PyUnreachableCode
    asyncio.run(main())
