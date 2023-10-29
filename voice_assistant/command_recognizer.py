from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer
from voice_assistant.app_interfaces.i_topic_definer import ITopicDefiner


class CommandRecognizer:
    """Определяет интерфейс класса, который определяет к какой теме принадлежит команда"""

    def __init__(self, topic_definer: ITopicDefiner):
        self._topic_definer = topic_definer

        self._command_dict: dict[str, ICommandPerformer] = {}
        self._default_command: ICommandPerformer | None = None

    def add_command(self, command_class: ICommandPerformer):
        """Добавляет команды для распознавания. Для задания команды по-умолчанию, нужно передать команду с текстом None"""
        topic = command_class.get_command_topic()
        if not topic:
            self._default_command = command_class
            return
        self._command_dict[topic] = command_class

    async def process_command(self, command_text: str) -> str | None:
        res = await self._process_command_from_dict(command_text)

        if res is None and self._default_command:
            res = await self._default_command.perform_command(command_text)

        return res

    async def _process_command_from_dict(self, command_text: str) -> str | None:
        topics = list(self._command_dict.keys())

        command_topic = await self._topic_definer.define_topic(topics, command_text)

        if command_topic is None:
            # print(f"Не услышал команд, которые я знаю: {command_text}")
            return

        assert command_topic in topics, "ITopicDefiner отработал неправильно"

        command_performer = self._command_dict[command_topic]

        command_text = command_text[len(command_topic) :].strip()
        command_res = await command_performer.perform_command(command_text)

        return command_res
