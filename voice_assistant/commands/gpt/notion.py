import asyncio
import os

# from notion.client import NotionClient
from pytion import Notion
from pytion.api import Element
from pytion.models import Block

from voice_assistant.app_interfaces import ITopicDefiner
from voice_assistant.app_interfaces.i_command_performer import ICommandPerformer
from voice_assistant.topic_definers.gpt.gpt_modules.i_gpt_module import IGPTModule

PROMPT_DELETE_TOPIC_FROM_TEXT = """\
Удали из предложения "{note}" упоминание о "{topic}" и вышли мне исправленный вариант.\
"""


class CommandGPTNotion(ICommandPerformer):
    _prompt_delete_topic_from_text = PROMPT_DELETE_TOPIC_FROM_TEXT

    def __init__(self, gpt_module: IGPTModule, topic_definer: ITopicDefiner):
        self.gpt_module = gpt_module
        self.topic_definer = topic_definer
        self._no: Notion = Notion(token=os.environ.get("TOKEN"))
        self._main_page = self._no.pages.get("0aaa8ebc4ae64937be87533d951df04c")

        return

    def get_command_topic(self) -> str:
        return "списки"

    async def perform_command(self, command_context: str) -> str | None:
        pages: Element = self._main_page.get_block_children()
        inner_pages = {p.text: p for p in pages.obj if p.type == "child_page"}

        # command_context = command_context[len(self.get_command_topic()):]
        if command_context == "":
            return
        suggested_topic = await self.topic_definer.define_topic(
            list(inner_pages.keys()), command_context
        )

        if suggested_topic is None:
            return f'Не знаю куда записать "{command_context}"'

        page_block: Block = inner_pages[suggested_topic]

        # page = self._no.pages.get(page_block.id)

        note_text = command_context
        note_text = self.gpt_module.get_answer(
            self._generate_prompt_delete_topic_from_text(note_text, suggested_topic)
        )

        my_text_block = Block.create(note_text)
        self._no.blocks.block_append(page_block.id, block=my_text_block)

        return f'Добавил "{command_context}" на страницу "{suggested_topic}"'

    def _generate_prompt_delete_topic_from_text(self, note: str, topic: str) -> str:
        prompt = self._prompt_delete_topic_from_text.format(
            note=note,
            topic=topic,
        )
        return prompt


if __name__ == "__main__":

    async def main():
        t = CommandGPTNotion(None, None)

        await t.perform_command("a")

    asyncio.run(main())
