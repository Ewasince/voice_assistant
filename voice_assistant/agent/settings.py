from pydantic import SecretStr

from voice_assistant.app_utils.base_settings import ExtendedSettings


class AgentSettings(ExtendedSettings):
    agent_model: str = "openai/gpt-4.1-mini"
    agent_api_key: SecretStr
    agent_api_base_url: str = "https://api.vsegpt.ru/v1"
    agent_session_name: str = "default_session"


# noinspection PyArgumentList
agent_settings = AgentSettings()
