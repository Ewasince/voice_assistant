from pydantic import SecretStr

from voxmind.app_utils.settings import Settings


class VASettings(Settings):
    debug_mode: bool = False

    langflow_flow_id: str
    langflow_session_id: str = "default_session"

    openai_model: str = "openai/gpt-4.1-mini"
    openai_api_key: SecretStr
    openai_api_base_url: str = "https://api.vsegpt.ru/v1"
    composio_api_key: SecretStr
