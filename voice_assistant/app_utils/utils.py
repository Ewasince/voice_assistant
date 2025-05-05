import re

from voice_assistant.app_utils.settings import Settings

config = Settings()
p = re.compile(config.regexp)


def normalize_text(input_text: str) -> str:
    text = input_text.lower()
    text = p.sub("", text)
    return text.strip()


def quote_list(entries: list[str]) -> str:
    return '"' + '", "'.join(entries) + '"'
