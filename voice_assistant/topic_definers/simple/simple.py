from voice_assistant.app_interfaces.topic_definer import TopicDefiner


class TopicDefinerSimple(TopicDefiner):
    async def define_topic(self, topics: list[str], current_topic: str) -> str | None:
        for command_topic in topics:
            if not current_topic.startswith(command_topic):
                continue
            break
        else:
            return None

        return command_topic
