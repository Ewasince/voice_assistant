from async_lru import alru_cache
from composio import Composio
from loguru import logger

from voice_assistant.app_utils.settings import get_settings


@alru_cache
async def create_composio(user_id: str) -> Composio:
    composio_settings = get_settings().composio_settings

    logger_ = logger.bind(user_id=user_id, activity="composio")
    composio: Composio = Composio(api_key=composio_settings.composio_api_key.get_secret_value())

    users = composio.connected_accounts.list().items

    toolkit = "googlecalendar"

    for user in users:
        if not user.model_extra:
            continue
        if user.model_extra["user_id"] != user_id:
            continue
        if user.status != "ACTIVE":
            continue
        if user.toolkit.slug != toolkit:
            continue
        return composio

    auth_request = composio.toolkits.authorize(
        user_id=user_id,
        toolkit=toolkit,
    )

    # Если нужен первый логин, у объекта будет redirect_url.
    if redirect_url := auth_request.redirect_url:
        logger_.info("Open link for authorize")
        logger_.info(redirect_url)

    # Вернётся сразу, если подключение уже существовало; иначе дождётся завершения OAuth.
    auth_request.wait_for_connection()
    logger_.info("composio instance created")

    return composio
