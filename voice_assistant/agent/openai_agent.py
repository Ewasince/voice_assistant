from agents import Agent, RunConfig, Runner, SQLiteSession, Tool
from agents.models.multi_provider import MultiProvider

from voice_assistant.agent.settings import agent_settings
from voice_assistant.app_utils.types import UserId
from voice_assistant.tools.tools_factory import get_tools


class UserAgent:
    def __init__(
        self,
        user_id: UserId,
        tools: list[Tool],
    ):
        self._agent = Agent(
            name="Personal AI assistant",
            instructions="You are a helpful assistant who can use tools to answer questions and perform tasks. "
            "In addition to simply using tools, you should also anticipate the needs of the person you "
            "are assisting. Tools are not just for completing tasks—they are ways to help their owner, "
            "keep records, and make notes. You should understand from the context which tool to use based "
            "on the potential desires or intentions of the owner. Also, when the owner provides "
            "information about what they are doing, you should record this activity using the appropriate "
            "tool.Answer in Russian",
            tools=tools,
        )

        self._session = SQLiteSession(UserAgent.get_session_name(user_id))

        # TODO: per-user models
        self._multi_provider = MultiProvider(
            openai_base_url=agent_settings.agent_api_base_url,
            openai_api_key=agent_settings.agent_api_key.get_secret_value(),
            openai_use_responses=False,
        )

        self._multi_provider._get_prefix_and_model_name = _get_prefix_and_model_name  # type: ignore[method-assign, assignment]

    async def run_agent(self, input_text: str) -> str | None:
        result = await Runner.run(
            starting_agent=self._agent,
            input=input_text,
            run_config=RunConfig(
                model=agent_settings.agent_model,
                model_provider=self._multi_provider,
                tracing_disabled=True,
            ),
            session=self._session,
        )
        output = result.final_output
        if not isinstance(output, str | None):
            raise ValueError(f"agent output has wrong type ({type(output)}): {output}")
        return output

    @staticmethod
    def get_session_name(user_id: UserId) -> str:
        return str(user_id)


# need to compatibility with vsegpt
def _get_prefix_and_model_name(full_model_name: str | None) -> tuple[str | None, str | None]:
    if full_model_name is None:
        return None, None
    if "/" in full_model_name:
        prefix, _ = full_model_name.split("/", 1)
        return prefix, full_model_name
    return None, full_model_name


async def get_agent(user_id: UserId) -> UserAgent:
    tools = await get_tools(user_id)
    return UserAgent(user_id, tools)
