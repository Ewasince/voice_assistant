from datetime import datetime, timedelta

from agents import Tool

from voice_assistant.app_interfaces.toolset import Toolset
from voice_assistant.app_utils.app_types import UserId
from voice_assistant.database.core import engine
from voice_assistant.database.models import Contex
from voice_assistant.services.calendar.calendar_data import CalendarDataService
from voice_assistant.services.calendar.creds import get_calendar_credentials
from voice_assistant.services.calendar.service import CalendarService
from voice_assistant.services.google_settings import calendar_settings
from voice_assistant.services.memory import ContextMemoryService
from voice_assistant.tools.utils import parse_datetime, parse_timedelta


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
            self.update_activity_in_memory,
            self.forget_saved_activity,
            self.get_saved_activity,
        )

    async def log_new_activity(
        self,
        new_activity_topic: str,
        new_activity_offset: str | None = None,
        new_activity_time: str | None = None,
    ) -> str:
        """Log a new activity event.
        Trigger this tool when the user indicates they are currently engaged in an activity, have just started one,
        or clearly stated that the activity began some time ago.
        Offset values must be in the %H:%M format, а positive value indicates a delta into the past
        (e.g., "01:10" means the activity started 1 hour and 10 minutes ago).

        Args:
            new_activity_topic: Name of the started activity. Should be short, precise, and sound natural to a human —
                like a familiar, conventional label for the activity. Avoid synonyms, verb forms, or uncommon phrasings.

            new_activity_offset: Time since activity started (optional). Provide this only if the user explicitly
                mentioned how long ago the activity began.

                Format must be "%H:%M".
            new_activity_time: Exact start time of the activity (optional). Provide this only if the user explicitly
                mentioned the specific time the activity began. The value must be in the "%H:%M" format (e.g., "14:35").
        """

        context = self._memory_service.load_contex()

        new_activity_delta = None
        if new_activity_offset is not None:
            new_activity_delta = parse_timedelta(new_activity_offset)

        response_message = ""
        current_time = datetime.now(tz=calendar_settings.calendar_tz)

        end_time = current_time

        if new_activity_delta is not None:
            end_time = current_time - new_activity_delta

        if new_activity_time is not None:
            end_time = parse_datetime(new_activity_time)

        last_activity_topic = context.last_activity_topic
        last_activity_time = context.last_activity_time
        if last_activity_topic and last_activity_time:
            if end_time < last_activity_time:
                end_time = last_activity_time + timedelta(minutes=1)
                response_message += (
                    "Время окончания оказалось меньше времени начала! Поставил время на своё усмотрение. "
                )
            await self._calendar_service.jot_down_activity(
                last_activity_topic,
                last_activity_time,
                end_time,
            )

            new_activity_message = f'Зафиксировал конец активности "{last_activity_topic}". '

            response_message += new_activity_message

        context.last_activity_topic = new_activity_topic
        context.last_activity_time = end_time

        response_message += f'Запомнил активность "{new_activity_topic}"'

        if new_activity_delta:
            delta_minutes = new_activity_delta.total_seconds() / 60
            response_message += f" {delta_minutes:.2f} минут назад. "
        else:
            response_message += ". "

        self._memory_service.save_contex(context)

        return response_message

    async def log_end_activity(
        self,
        end_activity_offset: str | None = None,
        end_activity_time: str | None = None,
    ) -> str:
        """Log an activity event that ended.
        Use this tool only if the user has stated that an activity is finished AND has NOT mentioned being currently
        engaged in another activity or just starting one.

        Args:
            end_activity_offset: Time since activity ended (optional). Provide this only if the user explicitly
                mentioned how long ago the activity ended.
                Offset values must be in the %H:%M format, а positive value indicates a delta into the past
                (e.g., "01:10" means the activity started 1 hour and 10 minutes ago).

            end_activity_time: Exact end time of the activity (optional). Provide this only if the user explicitly
                mentioned the specific time the activity began. The value must be in the "%H:%M" format (e.g., "14:35").
        """

        context = self._memory_service.load_contex()

        end_activity_delta = None
        if end_activity_offset is not None:
            end_activity_delta = parse_timedelta(end_activity_offset)

        response_message = ""
        current_time = datetime.now(tz=calendar_settings.calendar_tz)

        end_time = current_time

        if end_activity_delta is not None:
            end_time = current_time - end_activity_delta

        if end_activity_time is not None:
            end_time = parse_datetime(end_activity_time)

        last_activity_topic = context.last_activity_topic
        last_activity_time = context.last_activity_time

        if last_activity_topic and last_activity_time:
            if end_time < last_activity_time:
                end_time = last_activity_time + timedelta(minutes=1)
                response_message += (
                    "Время окончания оказалось меньше времени начала! Поставил время на своё усмотрение. "
                )
            await self._calendar_service.jot_down_activity(
                last_activity_topic,
                last_activity_time,
                end_time,
            )
        else:
            self._logger.error(f"commit end activity called without last activity {context}")

        context.last_activity_topic = None
        context.last_activity_time = None

        if last_activity_topic:
            new_activity_message = f'Зафиксировал конец активности "{last_activity_topic}"'

            if end_activity_delta:
                delta_minutes = end_activity_delta.total_seconds() / 60
                new_activity_message += f" {delta_minutes:.2f} минут назад. "
            else:
                new_activity_message += ". "

            response_message += new_activity_message
        else:
            response_message += "Не было информации о последней активности"

        self._memory_service.save_contex(context)

        return response_message

    async def update_activity_in_memory(
        self,
        activity_topic: str | None = None,
        activity_relative_offset: str | None = None,
        activity_offset_from_now: str | None = None,
    ) -> str:
        """Update details of a previously started activity with log_new_activity
        Offset values must be in the %H:%M format, а positive value indicates a delta into the past
        (e.g., "01:10" means the activity started 1 hour and 10 minutes ago).

        Args:
            activity_topic: (Optional) Updated name of the saved activity. Should be short, precise, and sound natural
                to a human — like a familiar, conventional label for the activity. Avoid synonyms, verb forms, or
                uncommon phrasings.
                Provide only if the user wants to rename the remembered activity.

            activity_relative_offset: (Optional) Relative shift to adjust the original
                start time. Format must be "%H:%M".
                Use this only if the user wants to move the start time by a specific amount.

            activity_offset_from_now: (Optional) Sets the start time to a point relative to the current time.
                Format must be "%H:%M".
                Use this when the user indicates how long ago the activity started, relative to the present moment.

        Notes:
            - Only provide parameters that the user intends to change.
            - Only one time-related parameter should be provided at a time. If more than one is given, the input is
                considered invalid.
        """
        response_message = ""

        context = self._memory_service.load_contex()
        current_time = datetime.now(tz=calendar_settings.calendar_tz)

        new_last_activity_time = None
        if activity_relative_offset is not None and context.last_activity_time is not None:
            new_last_activity_time = context.last_activity_time - parse_timedelta(activity_relative_offset)
        elif activity_offset_from_now is not None:
            new_last_activity_time = current_time - parse_timedelta(activity_offset_from_now)

        if new_last_activity_time:
            context.last_activity_time = new_last_activity_time
            response_message += f"Перенёс активность на {new_last_activity_time.strftime('%H:%M')}. "

        if activity_topic:
            context.last_activity_topic = activity_topic
            response_message += f"Переименовал активность на {activity_topic}. "

        self._memory_service.save_contex(context)

        return response_message

    async def forget_saved_activity(
        self,
    ) -> str:
        """Use this tool when the user clearly states they want to cancel, delete, or forget an activity that was
        previously logged. Do not use when the activity simply ends — use only if the user requests its removal
        or negation.
        """
        response_message = ""

        context = self._memory_service.load_contex()
        self._memory_service.save_contex(Contex())

        response_message += f"Отменил активность {context.last_activity_topic}"

        return response_message

    async def get_saved_activity(
        self,
    ) -> str:
        """Retrieve information about the currently logged activity.
        Use this tool when the user asks to view or recall what activity is currently saved in memory or what activity
        is active.
        This refers only to the explicitly stored activity via log_new_activity tool — not to general past mentions
        in conversation.
        """
        response_message = ""

        current_time = datetime.now(tz=calendar_settings.calendar_tz)

        context = self._memory_service.load_contex()

        last_activity_time = context.last_activity_time
        last_activity_topic = context.last_activity_topic

        if last_activity_time is None and last_activity_topic is None:
            response_message += "Сейчас не запомнено активности"
        elif last_activity_time is None:
            response_message += f"Сейчас запомнена активность с темой '{last_activity_topic}'. "
        elif last_activity_topic is None:
            activity_delta = current_time - last_activity_time
            delta_minutes = activity_delta.total_seconds() / 60

            response_message += f"Сейчас запомнена активность которая началась {delta_minutes:.2f} минут назад."
        else:
            activity_delta = current_time - last_activity_time
            delta_minutes = activity_delta.total_seconds() / 60

            response_message += (
                f"Сейчас запомнена активность с темой '{context.last_activity_topic}', "
                f"которая началась {delta_minutes:.2f} минут назад."
            )

        return response_message


async def get_activity_logger(user_id: UserId) -> ActivityLoggerToolset:
    calendar_data_service = CalendarDataService(engine, user_id)
    creds = await get_calendar_credentials(calendar_data_service)

    user_data = calendar_data_service.load_calendar_data()

    if user_data is None:
        raise RuntimeError(f"has no calendar data for {user_id.log()}")

    calendar_service = CalendarService(user_id, creds, user_data.calendar_id)

    return ActivityLoggerToolset(user_id, calendar_service)
