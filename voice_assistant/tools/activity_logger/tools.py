from datetime import datetime

from agents import Tool

from voice_assistant.app_interfaces.toolset import Toolset
from voice_assistant.app_utils.types import UserId
from voice_assistant.database.core import engine
from voice_assistant.database.models import Contex
from voice_assistant.services.calendar.calendar_data import CalendarDataService
from voice_assistant.services.calendar.creds import get_calendar_credentials
from voice_assistant.services.calendar.service import CalendarService
from voice_assistant.services.calendar.settings import calendar_settings
from voice_assistant.services.memory import ContextMemoryService


class ActivityLoggerToolset(Toolset):
    def __init__(self, user_id: UserId, calendar_service: CalendarService) -> None:
        super().__init__()
        self._user_id = user_id
        self._calendar_service: CalendarService = calendar_service

        self._memory_service = ContextMemoryService(user_id)

        self._logger = self._logger.bind(user_id=user_id)

    async def get_tools(self) -> list[Tool]:
        return self._wrap_tools(
            self.log_new_activity,
            self.log_end_activity,
            self.cancel_activity,
        )

    async def log_new_activity(
        self,
        new_activity_topic: str,
        new_activity_offset: str | None = None,  # noqa: ARG002
    ) -> str:
        """Log a new activity event.
        Trigger this tool when the user indicates they are currently engaged in an activity or have just started one.

        Args:
            new_activity_topic: Name of the started activity. Should be short, precise, and sound natural to a human —
                like a familiar, conventional label for the activity. Avoid synonyms, verb forms, or uncommon phrasings.
            new_activity_offset: Time since activity started (optional). Provide this only if the user explicitly
                mentioned how long ago the activity began. The value must be in the %H:%M:%S format —
                for example: "00:10:45" (10 minutes and 45 seconds ago).
        """

        context = self._memory_service.load_contex()

        response_message = ""
        try:
            current_time = datetime.now(tz=calendar_settings.calendar_tz)

            last_activity_topic = context.last_activity_topic
            last_activity_time = context.last_activity_time
            if last_activity_topic and last_activity_time:
                await self._calendar_service.jot_down_activity(
                    last_activity_topic,
                    last_activity_time,
                    current_time,
                )
                response_message += f'Зафиксировал активность "{last_activity_topic}". '

            context.last_activity_topic = new_activity_topic
            context.last_activity_time = current_time

            response_message += f'Запомнил активность "{new_activity_topic}". '
        except Exception as e:
            response_message += f"Возникла ошибка: {e}"

        self._memory_service.save_contex(context)

        return f"Передай пользователю — {response_message}"

    async def log_end_activity(
        self,
        end_activity_offset: str | None = None,  # noqa: ARG002
    ) -> str:
        """Log an activity event that ended.
        Use this tool only if the user has stated that an activity is finished AND has NOT mentioned being currently
        engaged in another activity or just starting one.

        Args:
            end_activity_offset: Time since activity ended (optional). Provide this only if the user explicitly
                mentioned how long ago the activity ended. The value must be in the %H:%M:%S format —
                for example: "00:10:45" (10 minutes and 45 seconds ago).
        """

        context = self._memory_service.load_contex()

        response_message = ""
        try:
            current_time = datetime.now(tz=calendar_settings.calendar_tz)

            last_activity_topic = context.last_activity_topic
            last_activity_time = context.last_activity_time

            if last_activity_topic and last_activity_time:
                await self._calendar_service.jot_down_activity(
                    last_activity_topic,
                    last_activity_time,
                    current_time,
                )
            else:
                self._logger.error(f"commit end activity called without last activity {context}")

            context.last_activity_topic = None
            context.last_activity_time = None

            if last_activity_topic:
                response_message += f'Зафиксировал конец активности "{last_activity_topic}"'
            else:
                response_message += "Не было информации о последней активности"
        except Exception as e:
            response_message += f"Возникла ошибка: {e}"

        self._memory_service.save_contex(context)

        return f"Передай пользователю — {response_message}"

    async def cancel_activity(
        self,
    ) -> str:
        """Use this tool when the user clearly states they want to cancel, delete, or forget an activity that was
        previously stored. Do not use when the activity simply ends — use only if the user requests its removal
        or negation.
        """
        response = ""

        context = self._memory_service.load_contex()
        self._memory_service.save_contex(Contex())

        response += f"Отменил активность {context.last_activity_topic}"

        return f"Сообщи пользователю что ты — {response}"


async def get_activity_logger(user_id: UserId) -> ActivityLoggerToolset:
    calendar_data_service = CalendarDataService(engine, user_id)
    creds = await get_calendar_credentials(calendar_data_service)

    user_data = calendar_data_service.load_calendar_data()

    if user_data is None:
        raise RuntimeError(f"has no calendar data for {user_id.log()}")

    calendar_service = CalendarService(user_id, creds, user_data.calendar_id)

    return ActivityLoggerToolset(user_id, calendar_service)
