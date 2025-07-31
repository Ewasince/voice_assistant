from pydantic import SecretStr

from voxmind.app_utils.settings import Settings


class VASettings(Settings):
    debug_mode: bool = False

    langflow_flow_id: str
    langflow_session_id: str = "default_session"

    agent_model: str = "openai/gpt-4.1-mini"
    agent_api_key: SecretStr
    agent_api_base_url: str = "https://api.vsegpt.ru/v1"
    agent_session_name: str = "default_session"

    # database
    database_uri: str = "sqlite:///data/data.db"

    composio_api_key: SecretStr
