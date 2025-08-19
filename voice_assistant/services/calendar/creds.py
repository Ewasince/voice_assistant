import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from loguru import logger

from voice_assistant.database.calendar_data.calendar_data import CalendarDataService
from voice_assistant.services.google_settings import calendar_settings


class NoCalendarDataError(ValueError):
    pass


async def get_calendar_credentials(calendar_data_service: CalendarDataService, refresh: bool = False) -> Credentials:
    calendar_data = calendar_data_service.load_calendar_data()

    if calendar_data is None:
        raise NoCalendarDataError(f"no calendar_data found for user_id='{calendar_data_service.user_id}'")

    creds = None

    # 1) Пробуем загрузить сохранённые токены
    if calendar_data.token_data and not refresh:
        creds = Credentials.from_authorized_user_info(
            info=calendar_data.token_data,
            scopes=calendar_settings.google_scopes,
        )

    # 2) Если токен валиден — возвращаем его
    if creds and creds.valid:
        return creds

    user_id = calendar_data_service.user_id
    if creds and creds.expired and creds.refresh_token:
        logger.bind(user_id=user_id).info("Refreshing Google OAuth token...")
        creds.refresh(Request())
    else:
        logger.bind(user_id=user_id).info("Running OAuth flow in browser...")

        # Используем creds_data напрямую (dict)
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=calendar_settings.calendar_creds_file,
            scopes=calendar_settings.google_scopes,
        )

        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    # 3) Сохраняем токен обратно в БД
    calendar_data.token_data = json.loads(creds.to_json())
    calendar_data_service.save_calendar_data(calendar_data)

    return creds
