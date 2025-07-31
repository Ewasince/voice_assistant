from agents import Agent, RunConfig, Runner, SQLiteSession
from agents.models.multi_provider import MultiProvider

from voice_assistant.settings import VASettings
from voice_assistant.tools.activity_logger.tools import log_end_activity, log_new_activity

settings = VASettings()

agent = Agent(
    name="Personal AI assistant",
    instructions="You are a helpful assistant who can use tools to answer questions and perform tasks.In addition to "
    "simply using tools, you should also anticipate the needs of the person you are assisting. Tools are "
    "not just for completing tasks—they are ways to help their owner, keep records, and make notes. You "
    "should understand from the context which tool to use based on the potential desires or intentions of "
    "the owner. Also, when the owner provides information about what they are doing, you should record "
    "this activity using the appropriate tool.Answer in Russian",
    tools=[
        log_new_activity,
        log_end_activity,
    ],
)

session = SQLiteSession(settings.agent_session_name)


multi_provider = MultiProvider(
    openai_base_url=settings.agent_api_base_url,
    openai_api_key=settings.agent_api_key.get_secret_value(),
    openai_use_responses=False,
)


# need to compatibility with vsegpt
def _get_prefix_and_model_name(full_model_name: str | None) -> tuple[str | None, str | None]:
    if full_model_name is None:
        return None, None
    if "/" in full_model_name:
        prefix, _ = full_model_name.split("/", 1)
        return prefix, full_model_name
    return None, full_model_name


multi_provider._get_prefix_and_model_name = _get_prefix_and_model_name  # type: ignore[method-assign, assignment]


async def run_agent(text: str) -> str:
    result = await Runner.run(
        starting_agent=agent,
        input=text,
        run_config=RunConfig(
            model=settings.agent_model,
            model_provider=multi_provider,
            tracing_disabled=True,
        ),
        session=session,
    )
    return result.final_output
