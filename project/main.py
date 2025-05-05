import asyncio
from typing import NoReturn

from voice_assistant.commands.gpt.default import CommandGPTDefault
from voice_assistant.commands.gpt.notion import CommandGPTNotion


async def main() -> NoReturn:
    # создаём объект распознавания голоса, который будет переводить наш голос в текст
    from voice_assistant.app_interfaces import TextSource
    from voice_assistant.message_recognizers.text_source_local_mic import TextSourceLocalMic

    messages_recognizer: TextSource = TextSourceLocalMic()

    # создаём объект источника команд, который будет предварительно обрабатывать команды
    from voice_assistant.message_source import MessageSource

    message_source = MessageSource(messages_recognizer)

    # создаём объект распознавателя команд
    # и передаём в него модуль, который будет определять к какой теме относится команда
    # так же передаём в модуль определния топика с помощью GPT объект GPT
    from voice_assistant.command_recognizer import CommandRecognizer
    from voice_assistant.app_interfaces import ITopicDefiner
    from voice_assistant.topic_definers.gpt.gpt import TopicDefinerGPT
    from voice_assistant.topic_definers.gpt.gpt_modules.i_gpt_module import IGPTModule
    from voice_assistant.topic_definers.gpt.gpt_modules.yagpt_module import YaGPTModule

    gpt_module: IGPTModule = YaGPTModule()

    topic_definer: ITopicDefiner = TopicDefinerGPT(gpt_module)
    command_recognizer: CommandRecognizer = CommandRecognizer(topic_definer)

    ### commands
    # так же добавляем команды. Каждая команда – это класс, который должен реализовывать интерфейс команды
    from voice_assistant.app_interfaces import ICommandPerformer
    from voice_assistant.commands import CommandGetCurrentOS
    from voice_assistant.commands import CommandGetCurrentTime

    command_time: ICommandPerformer = CommandGetCurrentOS()
    command_recognizer.add_command(command_time)

    command_time: ICommandPerformer = CommandGetCurrentTime()
    command_recognizer.add_command(command_time)

    command_notion: ICommandPerformer = CommandGPTNotion(gpt_module, topic_definer)
    command_recognizer.add_command(command_notion)

    command_default: ICommandPerformer = CommandGPTDefault(gpt_module)
    command_recognizer.add_command(command_default)

    ### main process
    # и, например, в цикле получаем от источника команд текстовые сообщения и обрабатываем их
    while True:
        command = await message_source.wait_command()
        res = await command_recognizer.process_command(command)

        if res is not None:
            print(res)


async def main2():
    # создаём объект распознавания голоса, который будет переводить наш голос в текст
    from voice_assistant.app_interfaces import TextSource

    messages_recognizer: TextSource = MessageRecognizerLocalMic()

    # создаём объект источника команд, который будет предварительно обрабатывать команды
    from voice_assistant import MessageSource

    message_source: MessageSource = MessageSource(messages_recognizer)

    # создаём объект распознавателя команд
    # и передаём в него модуль, который будет определять к какой теме относится команда
    from voice_assistant import CommandRecognizer
    from voice_assistant.app_interfaces import ITopicDefiner
    from voice_assistant.topic_definers import TopicDefinerSimple

    topic_definer: ITopicDefiner = TopicDefinerSimple()
    command_recognizer: CommandRecognizer = CommandRecognizer(topic_definer)

    ### commands
    # так же добавляем команды. Каждая команда – это класс, который должен реализовывать интерфейс команды
    from voice_assistant.app_interfaces import ICommandPerformer
    from voice_assistant.commands import CommandGetCurrentOS
    from voice_assistant.commands import CommandGetCurrentTime

    command_time: ICommandPerformer = CommandGetCurrentOS()
    command_recognizer.add_command(command_time)

    command_time: ICommandPerformer = CommandGetCurrentTime()
    command_recognizer.add_command(command_time)

    ### main process
    # и, например, в цикле получаем от источника команд текстовые сообщения и обрабатываем их
    while True:
        command = await message_source.wait_command()
        res = await command_recognizer.process_command(command)

        if res is not None:
            print(res)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Goodbye!")
