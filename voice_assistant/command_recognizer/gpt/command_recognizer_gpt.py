from voice_assistant.app_interfaces.i_command_recognizer import ICommandRecognizer
from voice_assistant.app_utils.utils import normalize_text
from voice_assistant.command_recognizer.gpt.gigachat_module import GigaChatModule
from voice_assistant.command_recognizer.gpt.i_gpt_module import IGPTModule
from voice_assistant.command_recognizer.gpt.yagpt_module import YaGPTModule

PROMT_DEFINE_TOPIC_YAGPT = '''\
У меня есть предложение "{sentence}", к какой из следующих тем оно относится – {command_topics}? Отправь мне одну из перечисленных тем без изменений.\
'''

PROMT_DEFINE_TOPIC_GIGACHAT = '''\
У меня есть предложение "{sentence}", к какой из следующих тем оно относится – {command_topics}? Отправь мне только название одной из тем БЕЗ ИЗМЕНЕНИЙ\
'''

PROMT_RELIABLE_TOPICS_YAGPT='''\
"{topic1}" и "{topic2}" это схожие по смыслу предложения? Ответь "да" или "нет"\
'''

class CommandRecognizerGPT(ICommandRecognizer):
    _promt_define_topic = PROMT_DEFINE_TOPIC_YAGPT
    _promt_define_reliable_topics = PROMT_RELIABLE_TOPICS_YAGPT

    def __init__(self, gpt_module: IGPTModule, promt: str = None):
        super().__init__()
        self.gpt_module = gpt_module

        if promt: self._promt_define_topic = promt
        return

    async def process_command_from_dict(self, command_text: str) -> str | None:

        command_topics = list(self._command_dict.keys())
        command_topics = self._prepare_command_topics(command_topics)

        promt = self._generate_promt_define_topic(command_topics, command_text)

        guess_topic = self.gpt_module.get_answer(promt)
        guess_topic = normalize_text(guess_topic)

        command_performer = self._command_dict.get(guess_topic, None)
        #

        if not command_performer:
            print(f'не нашёл к чему относится, пробую разобраться: "{guess_topic}", "{command_text}"')


            for command_topic, command_performer in self._command_dict.items():
                promt_reliable_topics = self._generate_promt_reliable_topics(guess_topic, command_topic)

                binary_answer = self.gpt_module.get_answer(promt_reliable_topics)
                binary_answer = normalize_text(binary_answer)

                if binary_answer == 'да':
                    break
                elif binary_answer == 'нет':
                    continue
                else:
                    print(f'Я спросил у gpt "{promt_reliable_topics}", а он ответил "{binary_answer}" и я не понял')
                    continue
            else:
                print(f"Не услышал известной команды: {command_text}")
                return

        command_res = await command_performer.perform_command(command_text)

        return command_res

    def _prepare_command_topics(self, topics: list[str]) -> str:
        return "\"" + "\", \"".join(topics) + "\""

    def _generate_promt_define_topic(self, topics: str, command: str) -> str:
        promt = self._promt_define_topic.format(
            command_topics=topics,
            sentence=command,
        )
        return promt

    def _generate_promt_reliable_topics(self, topic1: str, topic2: str) -> str:
        promt = self._promt_define_reliable_topics.format(
            topic1=topic1,
            topic2=topic2,
        )
        return promt



if __name__ == '__main__':
    # gpt = GigaChatModule('YTA5M2MzYjYtOWRmMi00MDYyLWFiMTUtYjMzOGIwY2M1NGRmOjE4ZjAxYzYwLTVkODktNGFiOS1iMjk4LTlhYTk1YjhmMDc1OA==')
    gpt = YaGPTModule()


    c = CommandRecognizerGPT(gpt)

    command_topics = ["списки", "планирование времени"]
    command_topics = c._prepare_command_topics(command_topics)
    command_text = 'нужно записать в список покупок купить огурцы'
    promt = c._generate_promt_define_topic(command_topics, command_text)

    res1 = gpt.get_answer(promt)
    print('VARIANT 1')
    print(promt)
    print(res1)


    command_text = 'запиши купить огурцы'
    promt = c._generate_promt_define_topic(command_topics, command_text)

    res2 = gpt.get_answer(promt)
    print('VARIANT 2')
    print(promt)
    print(res2)


    command_text = 'надо на завтра поставить напоминание'
    promt = c._generate_promt_define_topic(command_topics, command_text)

    res3 = gpt.get_answer(promt)
    print('VARIANT 3')
    print(promt)
    print(res3)
