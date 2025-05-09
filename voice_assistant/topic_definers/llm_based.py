from typing import ClassVar, Final

from voice_assistant.app_interfaces.llm_module import LLMClient
from voice_assistant.app_interfaces.topic_definer import TopicDefiner
from voice_assistant.app_utils.utils import normalize_text

_DEFINE_TOPIC_PROMPT_TEMPLATE: Final[str] = """\
Укажи, к какой из следующих тем относится предложение: "{sentence}".
Темы: {command_topics}
Ответь точно ОДНОЙ из этих тем БЕЗ ИЗМЕНЕНИЙ, если она подходит.
Если ни одна тема не подходит, просто напиши: "не знаю".
"""

_PROMPT_RELIABLE_TOPICS_TEMPLATE: Final[str] = """\
"{topic1}" и "{topic2}" это схожие по смыслу предложения? Ответь "да" или "нет"\
"""


class TopicDefinerGPT(TopicDefiner):
    _define_topic_prompt_template: ClassVar[str] = _DEFINE_TOPIC_PROMPT_TEMPLATE
    _define_reliable_topics_prompt_template: ClassVar[str] = _PROMPT_RELIABLE_TOPICS_TEMPLATE

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    async def choose_topic_from_list(self, topics: list[str], guessable_topic: str) -> str | None:
        prompt = self._generate_define_topic_prompt(topics, guessable_topic)

        guessed_topic = self._llm_client.get_answer(prompt)
        guessed_topic = normalize_text(guessed_topic)

        if guessed_topic in topics:
            return guessed_topic

        return None

        # TODO: хз пока оставлять ли логику усиленной проверки
        # print(
        #     f"не нашёл к чему относится, пробую разобраться. "
        #     f'Что я отгадал: "{guessed_topic}", что мне нужно отгадать: "{guessable_topic}"'
        # )
        # guessed_topic = self._define_reliable_topics(topics, guessed_topic)
        #
        # if guessed_topic in topics:
        #     return guessed_topic
        #
        # print(f"Не услышал известной команды: {guessable_topic}")
        # return None

    #
    # def _define_reliable_topics(self, topics: list[str], guess_topic: str) -> str | None:
    #     for command_topic in topics:
    #         prompt_reliable_topics = self._generate_prompt_reliable_topics(guess_topic, command_topic)
    #
    #         binary_answer = self._llm_client.get_answer(prompt_reliable_topics)
    #         binary_answer = normalize_text(binary_answer)
    #
    #         if binary_answer == "да":
    #             break
    #         if binary_answer == "нет":
    #             continue
    #         print(f'Я спросил у gpt "{prompt_reliable_topics}", а он ответил "{binary_answer}" и я не понял')
    #         continue
    #     else:
    #         return

    def _generate_define_topic_prompt(self, topics: list[str], command: str) -> str:
        topics_str = _make_bullet_list_from_str_list(topics)
        topics_str = f"\n{topics_str}"

        return self._define_topic_prompt_template.format(
            command_topics=topics_str,
            sentence=command,
        )

    def _generate_prompt_reliable_topics(self, topic1: str, topic2: str) -> str:
        return self._define_reliable_topics_prompt_template.format(
            topic1=topic1,
            topic2=topic2,
        )


def _make_bullet_list_from_str_list(items: list[str]) -> str:
    return "".join(f" * {item}\n" for item in items)
