from voice_assistant.agent.openai_agent import run_agent
from voice_assistant.settings import VASettings

settings = VASettings()


async def process_command(command_text: str) -> str:
    command_result = await run_agent(command_text)

    assistant_response = f"Ответ ассистента > {command_result}"

    if command_result is not None:
        print(assistant_response)
    else:
        print()

    return command_result
