from composio import Composio
from openai import OpenAI

from voice_assistant.settings import VASettings

settings = VASettings()

composio: Composio = Composio(api_key=settings.composio_api_key.get_secret_value())


user_id = "default"
toolkit = "googlecalendar"
# connected_accounts = composio.connected_accounts.list(user_ids=[user_id], toolkit_slugs=[toolkit])


# if not connected_accounts.items:
#     connection_request = composio.toolkits.authorize(
#         user_id=user_id,
#         toolkit=toolkit,
#         # tools=["gmail.read", "gmail.send"]  # или нужные тебе tool slugs
#     )
#
#     # Redirect user to the OAuth flow
#     redirect_url = connection_request.redirect_url
#
#     print(redirect_url)  # Print the redirect url to the user
#
#     # Wait for the connection to be established
#     connection_request.wait_for_connection()

# Initialize openai client.
openai_client = OpenAI(api_key=settings.openai_api_key.get_secret_value(), base_url=settings.openai_api_base_url)

# Get Gmail tools that are pre-configured
tools = composio.tools.get(user_id="default", tools=["GOOGLECALENDAR_EVENTS_LIST"])
# tools = composio.tools.get(user_id="default", tools=["GMAIL_SEND_EMAIL"])

# Get response from the LLM
response = openai_client.chat.completions.create(
    model=settings.openai_model,
    tools=tools,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": (
                "Send an email to ewasince@gmail.com with the subject 'Hello from composio 👋🏻' and "
                "the body 'Congratulations on sending your first email using AI Agents and Composio!'"
            ),
        },
    ],
)
print(response)

# Execute the function calls.
result = composio.provider.handle_tool_calls(response=response, user_id="default")
print(result)

if __name__ == "__main__":
    pass

# class GetIssueInfoInput(BaseModel):
#     issue_number: int = Field(
#         ...,
#         description="The number of the issue to get information about",
#     )
#
# # function name will be used as slug
# @composio.tools.custom_tool(toolkit="github")
# def get_issue_info(
#     request: GetIssueInfoInput,
#     execute_request: ExecuteRequestFn,
#     auth_credentials: dict,
# ) -> dict:
#     """Get information about a GitHub issue."""
#     response = execute_request(
#         endpoint=f"/repos/composiohq/composio/issues/{request.issue_number}",
#         method="GET",
#         parameters=[
#             {
#                 "name": "Accept",
#                 "value": "application/vnd.github.v3+json",
#                 "type": "header",
#             },
#             {
#                 "name": "Authorization",
#                 "value": f"Bearer {auth_credentials['access_token']}",
#                 "type": "header",
#             },
#         ],
#     )
#     return {"data": response.data}
