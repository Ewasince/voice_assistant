import re

from voice_assistant.app_utils.settings import primary_settings

p = re.compile(primary_settings.regexp)


def normalize_text(input_text: str) -> str:
    text = input_text.lower()
    text = p.sub("", text)
    return text.strip()
