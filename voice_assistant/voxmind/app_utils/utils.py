import re

from voice_assistant.voxmind.app_utils.settings import Settings

config = Settings()
p = re.compile(config.regexp)


def is_forbidden_chars(text: str) -> bool:
    return bool(p.findall(text))


def normalize_text(input_text: str) -> str:
    text = input_text.lower()
    text = p.sub("", text)
    return text.strip()
