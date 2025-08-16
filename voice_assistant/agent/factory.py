from voice_assistant.app_interfaces.user_agent import UserAgent
from voice_assistant.app_utils.app_types import UserId
from voice_assistant.tools.factory import get_tools


async def get_agent(user_id: UserId) -> UserAgent:
    from voice_assistant.agent.openai_agent import OpenAIAgent  # noqa: PLC0415

    tools = await get_tools(user_id)
    return OpenAIAgent(user_id, tools)
