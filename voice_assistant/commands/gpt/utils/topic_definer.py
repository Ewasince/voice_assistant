from voice_assistant.topic_definers.gpt.gpt_modules.i_gpt_module import IGPTModule


class TopicDefiner:
    def __init__(self, gpt_module: IGPTModule):
        self.gpt_module = gpt_module
        return

    def define_topic(self, topics: list[str], current_topic: str) -> str | None:
        pass
