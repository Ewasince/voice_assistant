import re

from voice_assistant.app_utils.settings import Settings

config = Settings()
p = re.compile(config.regexp)


def extract_text_after_command(text: str, key: str) -> str | None:
    if key is None or key == "":
        return text.strip()

    pos = text.find(key)
    if pos == -1:
        return None

    pos = pos + len(key) + 1

    filtered_text = text[pos:]

    return filtered_text.strip()


def normalize_text(input_text: str) -> str:
    text = input_text.lower()
    text = p.sub("", text)
    text = text.strip()
    return text


def quote_list(entries: list[str]) -> str:
    return '"' + '", "'.join(entries) + '"'
