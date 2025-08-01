from pydantic import SecretStr
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    agent_model: str = "openai/gpt-4.1-mini"
    agent_api_key: SecretStr
    agent_api_base_url: str = "https://api.vsegpt.ru/v1"
    agent_session_name: str = "default_session"


# noinspection PyArgumentList
agent_settings = AgentSettings()
