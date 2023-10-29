from voice_assistant.app_interfaces.i_topic_definer import ITopicDefiner
from voice_assistant.app_utils.utils import normalize_text
from voice_assistant.topic_definers.gpt.gpt_modules.i_gpt_module import IGPTModule

PROMPT_DEFINE_TOPIC = """\
У меня есть предложение "{sentence}", к какой из следующих тем оно относится – {command_topics}? Отправь мне одну из перечисленных тем без изменений.\
"""

PROMPT_RELIABLE_TOPICS = """\
"{topic1}" и "{topic2}" это схожие по смыслу предложения? Ответь "да" или "нет"\
"""


class TopicDefinerGPT(ITopicDefiner):
    _prompt_define_topic = PROMPT_DEFINE_TOPIC
    _prompt_define_reliable_topics = PROMPT_RELIABLE_TOPICS

    def __init__(self, gpt_module: IGPTModule):
        self._gpt_module = gpt_module
        return

    async def define_topic(self, topics: list[str], guessable_topic: str) -> str | None:
        command_topics_str = self._prepare_command_topics(topics)
        prompt = self._generate_prompt_define_topic(command_topics_str, guessable_topic)

        guessed_topic = self._gpt_module.get_answer(prompt)
        guessed_topic = normalize_text(guessed_topic)

        if guessed_topic in topics:
            return guessed_topic

        print(
            f'не нашёл к чему относится, пробую разобраться: "{guessed_topic}" ?= "{guessable_topic}"'
        )
        guessed_topic = self._define_reliable_topics(topics, guessed_topic)

        if guessed_topic in topics:
            return guessed_topic

        print(f"Не услышал известной команды: {guessable_topic}")
        return None

    def _define_reliable_topics(
        self, topics: list[str], guess_topic: str
    ) -> str | None:
        for command_topic in topics:
            prompt_reliable_topics = self._generate_prompt_reliable_topics(
                guess_topic, command_topic
            )

            binary_answer = self._gpt_module.get_answer(prompt_reliable_topics)
            binary_answer = normalize_text(binary_answer)

            if binary_answer == "да":
                break
            elif binary_answer == "нет":
                continue
            else:
                print(
                    f'Я спросил у gpt "{prompt_reliable_topics}", а он ответил "{binary_answer}" и я не понял'
                )
                continue
        else:
            return

    def _prepare_command_topics(self, topics: list[str]) -> str:
        return '"' + '", "'.join(topics) + '"'

    def _generate_prompt_define_topic(self, topics: str, command: str) -> str:
        prompt = self._prompt_define_topic.format(
            command_topics=topics,
            sentence=command,
        )
        return prompt

    def _generate_prompt_reliable_topics(self, topic1: str, topic2: str) -> str:
        prompt = self._prompt_define_reliable_topics.format(
            topic1=topic1,
            topic2=topic2,
        )
        return prompt
