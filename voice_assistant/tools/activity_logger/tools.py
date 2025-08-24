from datetime import datetime, time, timedelta

from agents import Tool

from voice_assistant.app_interfaces.toolset import Toolset
from voice_assistant.app_utils.app_types import UserId
from voice_assistant.app_utils.settings import get_settings
from voice_assistant.database.models import Contex
from voice_assistant.services.calendar.service import CalendarService, get_duration
from voice_assistant.services.memory import ContextMemoryService
from voice_assistant.tools.utils import parse_datetime, parse_timedelta


class ActivityLoggerToolset(Toolset):
    def __init__(self, user_id: UserId, calendar_service: CalendarService) -> None:
        super().__init__()
        self._user_id = user_id
        self._calendar_service: CalendarService = calendar_service

        self._memory_service = ContextMemoryService(user_id)

        self._logger = self._logger.bind(user_id=user_id)
        self._tz = get_settings(user_id).calendar_settings.tz

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
        new_activity_end_time: str | None = None,
        reject_old_activity: bool = False,
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

            new_activity_time: Exact start time of the activity (optional). Provide this only if the user
                explicitly mentioned the specific time the activity began.
                The value must be in the "%H:%M" format (e.g., "14:35").

            new_activity_end_time: Exact end time of the activity (optional). Provide this only if the user explicitly
                mentioned the specific time the activity ends.
                The value must be in the "%H:%M" format (e.g., "14:35").

            reject_old_activity: End the previous activity (optional). Provide this only if the user explicitly
                mentioned the specific time the activity ends.
                The value must be in the "%H:%M" format (e.g., "14:35").
        """

        context = self._memory_service.load_contex()

        new_activity_delta = None
        if new_activity_offset is not None:
            new_activity_delta = parse_timedelta(new_activity_offset)

        response_message = ""
        current_time = datetime.now(tz=self._tz)

        new_activity_start_time = current_time

        if new_activity_delta is not None:
            new_activity_start_time = current_time - new_activity_delta

        if new_activity_time is not None:
            new_activity_start_time = parse_datetime(new_activity_time, self._tz)

        last_activity_topic = context.last_activity_topic
        last_activity_start_time = context.last_activity_time

        if new_activity_end_time is not None:
            is_last_activity_present = last_activity_topic and last_activity_start_time
            if is_last_activity_present and not reject_old_activity:
                response_message += (
                    f"Ты указал конец только что переданной активности, "
                    f"но сейчас уже записана активность {last_activity_topic}"
                    "Либо заверши/отмени текущую активность, либо явно укажи что нужно отменить предыдущую активность"
                )
                return response_message

            new_activity_end_time_dt = parse_datetime(new_activity_end_time, self._tz)
            duration = await self._calendar_service.jot_down_activity(
                new_activity_topic,
                new_activity_start_time,
                new_activity_end_time_dt,
            )
            response_message += (
                f'Зафиксировал активность "{last_activity_topic}" '
                f"{_get_str_time_range(new_activity_start_time, new_activity_end_time_dt)}"
                f"продолжительностью {_get_str_time_duration(duration)}. "
            )
            return response_message

        if last_activity_topic and last_activity_start_time:
            last_activity_end_time = new_activity_start_time

            last_activity_end_time, response_update = _change_end_time_if_need(
                last_activity_start_time,
                last_activity_end_time,
            )
            response_message += response_update

            duration = await self._calendar_service.jot_down_activity(
                last_activity_topic,
                last_activity_start_time,
                last_activity_end_time,
            )

            response_message += (
                f'Зафиксировал конец активности "{last_activity_topic}" '
                f"продолжительностью {_get_str_time_duration(duration)}. "
            )

        context.last_activity_topic = new_activity_topic
        context.last_activity_time = new_activity_start_time

        response_message = f'Запомнил активность "{new_activity_topic}"'
        response_message += f"{_str_delta_if_need(new_activity_delta)}. "

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
        current_time = datetime.now(tz=self._tz)

        end_time = current_time

        if end_activity_delta is not None:
            end_time = current_time - end_activity_delta

        if end_activity_time is not None:
            end_time = parse_datetime(end_activity_time, self._tz)

        last_activity_topic = context.last_activity_topic
        last_activity_start_time = context.last_activity_time

        if last_activity_topic and last_activity_start_time:
            end_time, response_update = _change_end_time_if_need(
                last_activity_start_time,
                end_time,
            )
            response_message += response_update

            duration = await self._calendar_service.jot_down_activity(
                last_activity_topic,
                last_activity_start_time,
                end_time,
            )

            response_message = (
                f'Зафиксировал конец активности "{last_activity_topic}" '
                f"продолжительностью {_get_str_time_duration(duration)}"
                f"{_str_delta_if_need(end_activity_delta)}. "
            )
        else:
            self._logger.warning(f"commit end activity called without last activity {context}")
            response_message += "Нет активности чтобы её завершить!"

        context.last_activity_topic = None
        context.last_activity_time = None

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
        current_time = datetime.now(tz=self._tz)

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

        current_time = datetime.now(tz=self._tz)

        context = self._memory_service.load_contex()

        last_activity_time = context.last_activity_time
        last_activity_topic = context.last_activity_topic

        if last_activity_time is None and last_activity_topic is None:
            response_message += "Сейчас не запомнено активности"
        elif last_activity_time is None:
            response_message += f"Сейчас запомнена активность с темой '{last_activity_topic}'. "
        elif last_activity_topic is None:
            activity_delta = current_time - last_activity_time
            response_message += f"Сейчас запомнена активность которая началась {_str_delta_if_need(activity_delta)}. "
        else:
            activity_delta = current_time - last_activity_time
            response_message += (
                f"Сейчас запомнена активность с темой '{context.last_activity_topic}', "
                f"которая началась {_str_delta_if_need(activity_delta)}. "
            )

        return response_message


def _russian_plural(n: int, one: str, few: str, many: str) -> str:
    n_abs = abs(n)
    last_two = n_abs % 100
    last = n_abs % 10

    if 11 <= last_two <= 14:
        return many
    if last == 1:
        return one
    if 2 <= last <= 4:
        return few
    return many


def _get_str_time_duration(duration: time, accusative: bool = False) -> str:
    message = ""
    if duration.hour:
        hour_plural = _russian_plural(
            duration.hour,
            "час",
            "часа",
            "часов",
        )
        message += f"{duration.hour} {hour_plural}"
    if duration.minute:
        minutes_plural = _russian_plural(
            duration.minute,
            "минуту" if accusative else "минута",
            "минуты",
            "минут",
        )
        message += f"{duration.minute} {minutes_plural}"
    return message


def _get_str_time_range(start_datetime: datetime, end_datetime: datetime) -> str:
    start_datetime_str = start_datetime.strftime("%H:%M:%S")
    end_datetime_str = end_datetime.strftime("%H:%M:%S")
    return f"с {start_datetime_str} по {end_datetime_str}"


def _change_end_time_if_need(start_time: datetime, end_time: datetime) -> tuple[datetime, str]:
    response_message = ""
    changed_end_time = end_time
    if changed_end_time < start_time:
        changed_end_time = start_time + timedelta(minutes=1)
        response_message = "Время окончания оказалось меньше времени начала! Поставил время на своё усмотрение. "
    return changed_end_time, response_message


def _str_delta_if_need(new_activity_delta: timedelta | None) -> str:
    if new_activity_delta:
        new_activity_duration = get_duration(new_activity_delta)
        return f" {_get_str_time_duration(new_activity_duration, accusative=True)} назад"
    return ""
