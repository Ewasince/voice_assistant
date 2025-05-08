from voice_assistant.app_interfaces.command_performer import ICommandPerformer
from voice_assistant.app_interfaces.topic_definer import ITopicDefiner


class CommandRecognizer:
    """Определяет интерфейс класса, который определяет к какой теме принадлежит команда"""

    def __init__(self, topic_definer: ITopicDefiner):
        self._topic_definer = topic_definer

        self._command_dict: dict[str, ICommandPerformer] = {}
        self._default_command: ICommandPerformer | None = None

    def add_command(self, command_class: ICommandPerformer) -> None:
        """
        Добавляет команды для распознавания.
        Для задания команды по-умолчанию, нужно передать команду с текстом None
        """

        topic = command_class.get_command_topic()
        if not topic:
            self._default_command = command_class
            return
        self._command_dict[topic] = command_class

    async def process_command_from_text(self, command_text: str) -> str | None:
        command_performer = await self._ques_command(command_text)

        return await command_performer.perform_command(command_text)

    async def _ques_command(self, command_text: str) -> ICommandPerformer:
        topics = list(self._command_dict.keys())
        command_topic = await self._topic_definer.define_topic(topics, command_text)

        if command_topic is None:
            # print(f"Не услышал команд, которые я знаю: {command_text}")
            return self._default_command

        if command_topic not in topics:
            msg = "ITopicDefiner отработал неправильно"
            raise ValueError(msg)

        return self._command_dict[command_topic]


def _delete_topic_from_command(command_text, command_topic) -> str:
    return command_text[len(command_topic) :].strip()
