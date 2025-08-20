from async_lru import alru_cache

from voice_assistant.app_interfaces.toolset import Toolset
from voice_assistant.app_utils.app_types import UserId
from voice_assistant.app_utils.settings import get_settings
from voice_assistant.services.calendar.service import CalendarService
from voice_assistant.services.composio.factory import create_composio


@alru_cache
async def get_activity_logger(user_id: UserId) -> Toolset:
    from voice_assistant.tools.activity_logger.tools import ActivityLoggerToolset  # noqa: PLC0415

    composio = await create_composio(user_id)

    calendar_service = CalendarService(user_id, get_settings(user_id).calendar_settings.calendar_id, composio)

    return ActivityLoggerToolset(user_id, calendar_service)
