from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, SecretStr

from voice_assistant.app_utils.settings_utils.common import ExtendedConfigDict


class AgentSettings(BaseModel):
    model_config: ClassVar[ExtendedConfigDict] = {
        "env_prefix": "AGENT_",
        "extra": "ignore",
    }
    agent_model: str = "openai/gpt-4.1-mini"
    agent_api_key: SecretStr
    agent_api_base_url: str = "https://api.vsegpt.ru/v1"
    agent_session_name: str = "default_session"
