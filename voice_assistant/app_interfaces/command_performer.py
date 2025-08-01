from abc import ABC, abstractmethod
from typing import Any, ClassVar

from voice_assistant.voxmind.assistant_core.context import Context


class CommandPerformer(ABC):
    """Определяет класс, содержащий в себе команду"""

    # command topic defines how llm will see this command
    _command_topic: ClassVar[str] = ""
    _context_class_type: ClassVar[type] = dict

    @property
    def command_topic(self) -> str:
        if self._command_topic is None:
            msg = f"command topic not set for {self.__class__.__name__}"
            raise ValueError(msg)

        return self._command_topic

    @abstractmethod
    async def perform_command(self, command_text: str, context: Context) -> str | None:
        """Метод выполняющий команду. Может менять своё поведение, в зависимости от переданного контекста.
        Возвращает текст и/или делает какие-либо изменения в системе.
        """
        raise NotImplementedError

    def _get_reliable_context(self, context: Context) -> Any:
        context_key = self._command_topic

        if context_key in context.command_notes:
            return context.command_notes[context_key]

        return self._reset_reliable_context(context)

    def _reset_reliable_context(self, context: Context) -> Any:
        context_key = self._command_topic

        command_context = self._context_class_type()
        context.command_notes[context_key] = command_context

        return command_context
