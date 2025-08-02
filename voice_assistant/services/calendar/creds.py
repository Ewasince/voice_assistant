import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from loguru import logger

from voice_assistant.services.calendar.calendar_data import CalendarDataService
from voice_assistant.services.calendar.settings import calendar_settings


async def get_calendar_credentials(calendar_data_service: CalendarDataService) -> Credentials:
    calendar_data = calendar_data_service.load_calendar_data()

    if calendar_data is None:
        raise ValueError(f"No calendar_data found for user_id={calendar_data_service.user_id}")

    creds = None

    # 1) Пробуем загрузить сохранённые токены
    if calendar_data.token_data:
        creds = Credentials.from_authorized_user_info(
            info=calendar_data.token_data,
            scopes=calendar_settings.calendar_scopes,
        )

    # 2) Если токен валиден — возвращаем его
    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        logger.info(f"Refreshing Google OAuth token for {calendar_data_service.user_id}...")
        creds.refresh(Request())
    else:
        logger.info(f"Running OAuth flow in browser for {calendar_data_service.user_id}...")

        # Используем creds_data напрямую (dict)
        flow = InstalledAppFlow.from_client_config(
            client_config=calendar_data.creds_data,
            scopes=calendar_settings.calendar_scopes,
        )

        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    # 3) Сохраняем токен обратно в БД
    calendar_data.token_data = json.loads(creds.to_json())
    calendar_data_service.save_calendar_data(calendar_data)

    return creds
