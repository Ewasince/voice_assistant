from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict

from voice_assistant.app_utils.settings_utils.common import HierarchicalSettings


class AgentSettings(HierarchicalSettings):
    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
    )
    model: str = "openai/gpt-4.1-mini"
    api_key: SecretStr
    api_base_url: str = "https://api.vsegpt.ru/v1"
    session_name: str = "default_session"
    context_limit: int | None = 10
