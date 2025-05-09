import os
from typing import ClassVar

# from notion.client import NotionClient
from pytion import Notion
from pytion.api import Element
from pytion.models import Block
from voxmind.app_interfaces.command_performer import CommandPerformer
from voxmind.app_interfaces.llm_module import LLMClient
from voxmind.app_interfaces.topic_definer import TopicDefiner
from voxmind.assistant_core.context import Context

PROMPT_DELETE_TOPIC_FROM_TEXT = """\
Удали из предложения "{note}" упоминание о "{topic}" и вышли мне исправленный вариант.\
"""


class CommandGPTNotion(CommandPerformer):
    _command_topic: ClassVar[str] = "списки"
    _prompt_delete_topic_from_text = PROMPT_DELETE_TOPIC_FROM_TEXT

    def __init__(self, gpt_module: LLMClient, topic_definer: TopicDefiner):
        self.gpt_module = gpt_module
        self.topic_definer = topic_definer
        self._no: Notion = Notion(token=os.environ.get("TOKEN"))
        self._main_page = self._no.pages.get("0aaa8ebc4ae64937be87533d951df04c")

    async def perform_command(self, command_text: str, _: Context) -> str | None:
        pages: Element = self._main_page.get_block_children()
        inner_pages = {p.text: p for p in pages.obj if p.type == "child_page"}

        # command_text = command_text[len(self.get_command_topic()):]
        if command_text == "":
            return None
        suggested_topic = await self.topic_definer.choose_topic_from_list(list(inner_pages.keys()), command_text)

        if suggested_topic is None:
            return f'Не знаю куда записать "{command_text}"'

        page_block: Block = inner_pages[suggested_topic]

        # page = self._no.pages.get(page_block.id)

        note_text = command_text
        note_text = self.gpt_module.get_simple_answer(
            self._generate_prompt_delete_topic_from_text(note_text, suggested_topic)
        )

        my_text_block = Block.create(note_text)
        self._no.blocks.block_append(page_block.id, block=my_text_block)

        return f'Добавил "{command_text}" на страницу "{suggested_topic}"'

    def _generate_prompt_delete_topic_from_text(self, note: str, topic: str) -> str:
        return self._prompt_delete_topic_from_text.format(
            note=note,
            topic=topic,
        )
