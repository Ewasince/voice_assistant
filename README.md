# Описание

Проект голосового ассистента

# Установка

```shell
pip install 'git+https://github.com/Ewasince/voice_assistant'
```

# Использовать как пакет

Пример кода:

```python
# создаём объект распознавания голоса, который будет переводить наш голос в текст
from voice_assistant.app_interfaces.i_messages_recognizer import IMessagesRecognizer
from voice_assistant.message_recognizer.local_mic.message_recognizer_local_mic import MessageRecognizerLocalMic

messages_recognizer: IMessagesRecognizer = MessageRecognizerLocalMic()

# создаём объект источника команд, который будет предварительно обрабатывать команды
from voice_assistant.app_interfaces.i_messages_source import IMessagesSource
from voice_assistant.massages_source.messages_source import MessagesSourceLocalMic

message_source: IMessagesSource = MessagesSourceLocalMic(messages_recognizer)

# создаём объект распознавания распознавателя команд
# на данный момент реализован только простой распознаватель команд
from voice_assistant.app_interfaces.i_command_recognizer import ICommandRecognizer
from voice_assistant.command_recognizer.simple.command_recognizer_simple import CommandRecognizerSimple

command_recognizer: ICommandRecognizer = CommandRecognizerSimple()

### commands
# так же добавляем команды. Каждая команда – это класс, котрый должен реализовывать интерфейс
from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer
from voice_assistant.commands.command_get_current_os.command_get_current_os import CommandGetCurrentOS
from voice_assistant.commands.command_get_current_time.command_get_current_time import CommandGetCurrentTime

command_time: ICommandPerformer = CommandGetCurrentOS()
command_recognizer.add_command(command_time)

command_time: ICommandPerformer = CommandGetCurrentTime()
command_recognizer.add_command(command_time)

### main process
# и, например, в цикле получаем от источника команд текстовые сообщения и обрабатываем их
while True:
    command = message_source.wait_command()
    res = command_recognizer.process_command(command)

    if res is not None:
        print(res)
```