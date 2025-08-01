from loguru import logger

from voice_assistant.voxmind.app_interfaces.command_performer import CommandPerformer
from voice_assistant.voxmind.app_interfaces.topic_definer import TopicDefiner
from voice_assistant.voxmind.app_utils.utils import is_forbidden_chars
from voice_assistant.voxmind.assistant_core.context import Context


class CommandRecognizer:
    """Определяет интерфейс класса, который определяет к какой теме принадлежит команда"""

    def __init__(self, topic_definer: TopicDefiner):
        self._topic_definer = topic_definer

        self._command_dict: dict[str, CommandPerformer] = {}
        self._default_command: CommandPerformer | None = None

        self._context: Context = Context()

    def add_command(self, command_topic: str | None, command_class: CommandPerformer) -> None:
        """
        Добавляет команды для распознавания.
        Для задания команды по-умолчанию, нужно передать команду с текстом None
        """

        if not command_topic:
            self._default_command = command_class
            logger.info(f'Add default command: "{command_class.__class__.__name__}"')
            return
        if is_forbidden_chars(command_topic):
            msg = f"topic cant contain forbidden characters: {command_topic}"
            raise ValueError(msg)
        if command_topic in self._command_dict:
            msg = f"duplicate command topic: {command_topic}"
            raise ValueError(msg)
        self._command_dict[command_topic] = command_class
        logger.info(f'Add command "{command_topic}":"{command_class.__class__.__name__}"')

    async def process_command_from_text(self, command_text: str) -> str | None:
        command_performer = await self._guess_command(command_text)

        if command_performer is None:
            return "Прости, я не понял чего ты хочешь. Попробуй переформулировать"

        return await command_performer.perform_command(command_text, self._context)

    async def _guess_command(self, command_text: str) -> CommandPerformer | None:
        topics = list(self._command_dict.keys())
        command_topic = await self._topic_definer.choose_topic_from_list(topics, command_text)

        logger.info(f"Guessed topic: {command_topic}")

        if command_topic is None:
            if not self._default_command:
                msg = "default command not defined"
                raise ValueError(msg)
            # print(f"Не услышал команд, которые я знаю: {command_text}")
            return self._default_command

        if command_topic not in topics:
            msg = (
                f"TopicDefiner has missed topic: {command_topic}, in text: {command_text} and aviable topics: {topics}"
            )
            logger.warning(msg)
            return None

        return self._command_dict[command_topic]


def _delete_topic_from_command(command_text: str, command_topic: str) -> str:
    return command_text[len(command_topic) :].strip()
