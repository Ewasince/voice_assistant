from voice_assistant.app_interfaces.gpt_module import LLMModule
from voice_assistant.app_interfaces.topic_definer import ITopicDefiner
from voice_assistant.app_utils.utils import normalize_text, quote_list

PROMPT_DEFINE_TOPIC = """\
У меня есть предложение "{sentence}", к какой из следующих тем оно относится \
– {command_topics}? Отправь мне одну из перечисленных тем без изменений. \
Если предложение ни к одной из тем не относится, напиши просто "не знаю".\
"""

PROMPT_RELIABLE_TOPICS = """\
"{topic1}" и "{topic2}" это схожие по смыслу предложения? Ответь "да" или "нет"\
"""


class TopicDefinerGPT(ITopicDefiner):
    _prompt_define_topic = PROMPT_DEFINE_TOPIC
    _prompt_define_reliable_topics = PROMPT_RELIABLE_TOPICS

    def __init__(self, gpt_module: LLMModule):
        self._gpt_module = gpt_module

    async def define_topic(self, topics: list[str], guessable_topic: str) -> str | None:
        command_topics_str = quote_list(topics)
        prompt = self._generate_prompt_define_topic(command_topics_str, guessable_topic)

        guessed_topic = self._gpt_module.get_answer(prompt)
        guessed_topic = normalize_text(guessed_topic)

        if guessed_topic in topics:
            return guessed_topic

        print(
            f"не нашёл к чему относится, пробую разобраться. "
            f'Что я отгадал: "{guessed_topic}", что мне нужно отгадать: "{guessable_topic}"'
        )
        guessed_topic = self._define_reliable_topics(topics, guessed_topic)

        if guessed_topic in topics:
            return guessed_topic

        print(f"Не услышал известной команды: {guessable_topic}")
        return None

    def _define_reliable_topics(self, topics: list[str], guess_topic: str) -> str | None:
        for command_topic in topics:
            prompt_reliable_topics = self._generate_prompt_reliable_topics(guess_topic, command_topic)

            binary_answer = self._gpt_module.get_answer(prompt_reliable_topics)
            binary_answer = normalize_text(binary_answer)

            if binary_answer == "да":
                break
            if binary_answer == "нет":
                continue
            print(f'Я спросил у gpt "{prompt_reliable_topics}", а он ответил "{binary_answer}" и я не понял')
            continue
        else:
            return

    def _generate_prompt_define_topic(self, topics: str, command: str) -> str:
        return self._prompt_define_topic.format(
            command_topics=topics,
            sentence=command,
        )

    def _generate_prompt_reliable_topics(self, topic1: str, topic2: str) -> str:
        return self._prompt_define_reliable_topics.format(
            topic1=topic1,
            topic2=topic2,
        )
