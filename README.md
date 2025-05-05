# Описание

Проект голосового ассистента

# Установка

```shell
pip install 'git+https://github.com/Ewasince/voice_assistant'
```

# Использовать как пакет

Пример кода:

```python
async def main():
    # создаём объект распознавания голоса, который будет переводить наш голос в текст
    # создаём объект распознавания голоса, который будет переводить наш голос в текст
    from voice_assistant.app_interfaces import TextSource
    from voice_assistant import MessageRecognizerLocalMic

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
            loguru.info(res)
```