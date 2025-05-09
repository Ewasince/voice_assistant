import asyncio
import sys
from typing import NoReturn

from loguru import logger

logger.remove()  # Удаляем стандартный вывод в stderr
logger.add(sys.stdout, level="DEBUG")  # Добавляем вывод в stdout


async def main() -> NoReturn:
    from voice_assistant.app_utils.settings import Settings

    settings = Settings()

    # create commands source iterator
    from voice_assistant.app_interfaces.command_iterator import CommandIterator
    from voice_assistant.commands_iterators.cli_command_iterator import CLICommandIterator

    command_iterator: CommandIterator = CLICommandIterator(settings=settings)

    # create llm module
    from voice_assistant.app_interfaces.llm_module import LLMClient
    from voice_assistant.llm_clients.gigachat_client import GigaChatClient

    gpt_module: LLMClient = GigaChatClient(Settings())

    # topic definer, which determines which command need to activate
    from voice_assistant.app_interfaces.topic_definer import TopicDefiner
    from voice_assistant.topic_definers.llm_based import TopicDefinerGPT

    topic_definer: TopicDefiner = TopicDefinerGPT(gpt_module)

    # create command recognizer, which recognize command by using topic definer
    from voice_assistant.assistant_core.command_recognizer import CommandRecognizer

    command_recognizer: CommandRecognizer = CommandRecognizer(topic_definer)

    ### commands
    from voice_assistant.app_interfaces.command_performer import CommandPerformer

    # так же добавляем команды. Каждая команда – это класс, который должен реализовывать интерфейс команды
    from voice_assistant.commands.test_commands.get_current_os import CommandGetCurrentOS

    command_os: CommandPerformer = CommandGetCurrentOS()
    command_recognizer.add_command(command_os.command_topic, command_os)

    from voice_assistant.commands.test_commands.get_current_time import CommandGetCurrentTime

    command_time: CommandPerformer = CommandGetCurrentTime()
    command_recognizer.add_command(command_time.command_topic, command_time)

    from voice_assistant.commands.gpt.time_keeper import CommandTimeKeeperGoogle

    command_tk: CommandPerformer = CommandTimeKeeperGoogle(gpt_module)
    command_recognizer.add_command(command_tk.command_topic, command_tk)

    # command_notion: ICommandPerformer = CommandGPTNotion(llm_client, topic_definer)
    # command_recognizer.add_command(command_notion)

    from voice_assistant.commands.gpt.llm_question import CommandLLMQuestion

    command_default: CommandPerformer = CommandLLMQuestion(gpt_module)
    command_recognizer.add_command(None, command_default)

    ### main process
    # и, например, в цикле получаем от источника команд текстовые сообщения и обрабатываем их
    command_text: str
    async for command_text in command_iterator:
        command_result = await command_recognizer.process_command_from_text(command_text)
        assistant_response = f"Ответ ассистента > {command_result}"

        if command_result is not None:
            print(assistant_response)
        else:
            print()


if __name__ == "__main__":
    # noinspection PyUnreachableCode
    asyncio.run(main())
