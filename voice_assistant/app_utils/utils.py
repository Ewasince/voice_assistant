import re

from voice_assistant.app_utils.settings import get_settings

p = re.compile(get_settings().regexp)


def normalize_text(input_text: str) -> str:
    text = input_text.lower()
    text = p.sub("", text)
    return text.strip()
