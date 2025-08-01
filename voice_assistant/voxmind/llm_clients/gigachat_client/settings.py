from pydantic import SecretStr
from pydantic_settings import BaseSettings


class GigachatSettings(BaseSettings):
    gigachat_token: SecretStr
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_model: str = "GigaChat-2"
