import re

from app_utils.config import Config

config = Config()
p = re.compile(config.regexp)


def extract_text_after_command(text: str, key: str) -> str | None:
    pos = text.find(key)
    if pos == -1:
        return None

    pos = pos + len(key) + 1

    filtered_text = text[pos:]

    return filtered_text


def normalize_text(input_text: str) -> str:
    text = input_text.lower()
    text = p.sub("", text)
    return text
