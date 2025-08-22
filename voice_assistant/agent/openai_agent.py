from typing import Any

from agents import Agent, RunConfig, Runner, SQLiteSession, Tool, TResponseInputItem
from agents.models.multi_provider import MultiProvider
from loguru import logger

from voice_assistant.app_interfaces.user_agent import UserAgent
from voice_assistant.app_utils.app_types import UserId
from voice_assistant.app_utils.settings import get_settings


class OpenAIAgent(UserAgent):
    def __init__(
        self,
        user_id: UserId,
        tools: list[Tool],
    ):
        agent_settings = get_settings(user_id).agent_settings
        self._agent = Agent(
            name="Personal AI assistant",
            instructions="You are a helpful assistant who can use tools to answer questions and perform tasks. "
            "In addition to simply using tools, you should anticipate the needs of the person you "
            "are assisting. Tools are not just for completing tasks—they are ways to help their owner, "
            "keep records, and make notes. You should understand from the context which tool to use based "
            "on the potential desires or intentions of the owner. "
            "Also, when the owner provides information about what they are doing, you should record this activity "
            "using the appropriate tool. Answer in Russian. DO NOT RECALL TOOLS AGAIN IF THEY HAVE RETURNED AN ERROR. "
            "\n"
            "Respond in moderation: by default—brief, friendly, and to the point. "
            "Provide detailed answers only when truly necessary. "
            "DO NOT ASK THE USER WHAT THEY WANT UNLESS IT IS EXPLICITLY REQUIRED TO COMPLETE THE TASK.",
            tools=tools,
        )

        self._session = LimitedSQLiteSession(
            OpenAIAgent.get_session_name(user_id),
            limit=agent_settings.context_limit,
        )

        # TODO: per-user models
        self._multi_provider = UniversalMultiProvider(
            openai_base_url=agent_settings.api_base_url,
            openai_api_key=agent_settings.api_key.get_secret_value(),
            openai_use_responses=False,
        )

        self._run_config = RunConfig(
            model=agent_settings.model,
            model_provider=self._multi_provider,
            tracing_disabled=True,
        )

        logger.bind(user_id=user_id).info(f"Initialized UserAgent llm='{agent_settings.model}' with {len(tools)} tools")

    async def run_agent(self, input_text: str) -> str | None:
        result = await Runner.run(
            starting_agent=self._agent,
            input=input_text,
            run_config=self._run_config,
            session=self._session,
        )
        output = result.final_output
        if not isinstance(output, str | None):
            raise ValueError(f"agent output has wrong type ({type(output)}): {output}")
        return output

    @staticmethod
    def get_session_name(user_id: UserId) -> str:
        return str(user_id)


class LimitedSQLiteSession(SQLiteSession):
    def __init__(self, *args: Any, limit: int | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._limit = limit

    async def get_items(self, _: int | None = None) -> list[TResponseInputItem]:
        return await super().get_items(self._limit)


class UniversalMultiProvider(MultiProvider):
    # need to compatibility with vsegpt
    def _get_prefix_and_model_name(self, full_model_name: str | None) -> tuple[str | None, str | None]:
        return None, full_model_name
