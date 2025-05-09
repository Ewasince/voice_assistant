from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Final

from loguru import logger

from voice_assistant.app_interfaces.command_performer import CommandPerformer
from voice_assistant.app_interfaces.llm_module import LLMClient
from voice_assistant.assistant_core.context import Context as GeneralContext

_ACTIVITY_END: Final[str] = "окончание"
_ACTIVITY_NOT_END: Final[str] = "не окончание"
_DEFINE_END_TASK_PROMPT: Final[str] = f"""\
Проанализируй следующее высказывание:

"{{sentence}}"

Определи, указывает ли оно на завершение какой-либо деятельности или события.
Если высказывание прямо или косвенно указывает на завершение действия, напиши строго "{_ACTIVITY_END}".
Если оно не указывает на завершение (например, описывает начало, процесс, паузу, продолжение и т.д.), \
напиши строго "{_ACTIVITY_NOT_END}".
Не добавляй никаких пояснений или комментариев — только одно из двух словосочетаний: \
"{_ACTIVITY_END}" или "{_ACTIVITY_NOT_END}".
"""

_DEFINE_TASK_TOPIC_PROMPT: Final[str] = """\
Прочитай следующее предложение:

"{sentence}"

Определи, о каком виде активности в нём идёт речь, и опиши эту активность 1–5 словами, используя краткие, \
точные формулировки. Не добавляй лишнего текста — только суть активности.
"""


@dataclass
class Contex:
    last_activity_topic: str | None = None
    last_activity_time: datetime | None = None


class CommandTimeKeeperGoogle(CommandPerformer):
    _command_topic: ClassVar[str] = "запись того чем занимаюсь"
    _context_class_type: ClassVar[type] = Contex

    _define_end_task_prompt: ClassVar[str] = _DEFINE_END_TASK_PROMPT
    _define_task_topic_prompt: ClassVar[str] = _DEFINE_TASK_TOPIC_PROMPT

    def __init__(self, gpt_module: LLMClient):
        self._llm_module = gpt_module

    async def perform_command(self, command_text: str, context: GeneralContext) -> str | None:
        activity_type = self._llm_module.get_answer(self._generate_define_activity_end_prompt(command_text))
        # topic = self._llm_module.get_answer(self._generate_define_task_topic_prompt(text_context))

        command_context: Contex = self._get_reliable_context(context)

        if activity_type == _ACTIVITY_NOT_END:
            return await self._commit_new_activity(command_text, command_context)

        if activity_type != _ACTIVITY_END:
            logger.warning(f"Unknown activity type ({activity_type}): {command_text}")
            return await self._commit_new_activity(command_text, command_context)

        if command_context.last_activity_topic:
            return await self._commit_end_activity(command_context)

        logger.warning(f"Noticed end activity without last activity: {command_text}")
        return await self._commit_new_activity(command_text, command_context)

    async def _commit_new_activity(self, command_text: str, command_context: Contex) -> str:
        current_time = datetime.now()  # noqa: DTZ005

        response_message = ""

        last_activity_topic = command_context.last_activity_topic
        last_activity_time = command_context.last_activity_time
        if last_activity_topic and last_activity_time:
            await self._jot_down_activity(
                last_activity_topic,
                last_activity_time,
                current_time,
            )
            response_message += f'Записал активность "{last_activity_topic}".'

        new_activity_topic = self._llm_module.get_answer(self._generate_define_task_topic_prompt(command_text))
        command_context.last_activity_topic = new_activity_topic
        command_context.last_activity_time = current_time

        response_message += f'Запомнил активность "{new_activity_topic}".'

        return response_message

    async def _commit_end_activity(self, command_context: Contex) -> str:
        current_time = datetime.now()  # noqa: DTZ005

        last_activity_topic = command_context.last_activity_topic
        last_activity_time = command_context.last_activity_time

        if last_activity_topic and last_activity_time:
            await self._jot_down_activity(
                last_activity_topic,
                last_activity_time,
                current_time,
            )
        else:
            logger.error(f"commit end activity called without last activity {command_context}")

        command_context.last_activity_topic = None
        command_context.last_activity_time = None

        last_topic = command_context.last_activity_topic
        return f'Записал активность "{last_topic}"'

    async def _jot_down_activity(
        self,
        topic: str,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        logger.info(f"Бот записал активность {topic} с {start_time} по {end_time}")

    def _generate_define_activity_end_prompt(self, command: str) -> str:
        return self._define_end_task_prompt.format(
            sentence=command,
        )

    def _generate_define_task_topic_prompt(self, command: str) -> str:
        return self._define_task_topic_prompt.format(
            sentence=command,
        )
