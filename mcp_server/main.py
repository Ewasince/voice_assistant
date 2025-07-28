from loguru import logger
from mcp.server.fastmcp import FastMCP

from mcp_server.al_modules.database import init_db, load_contex, save_contex
from mcp_server.al_modules.helpers import commit_end_activity, commit_new_activity


class MCPServer(FastMCP):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_tool(self.log_new_activity)
        self.add_tool(self.log_end_activity)

    async def log_new_activity(
        self,
        new_activity: str,
        new_activity_offset: str | None = None,
    ) -> str:
        """Log a new activity event.
        Trigger this tool when the user indicates they are currently engaged in an activity or have just started one.

        Args:
            new_activity: Name of the started activity. Should be short, precise, and sound natural to a human —
                like a familiar, conventional label for the activity. Avoid synonyms, verb forms, or uncommon phrasings.
            new_activity_offset: Time since activity started (optional). Provide this only if the user explicitly
                mentioned how long ago the activity began. The value must be in the %H:%M:%S format —
                for example: "00:10:45" (10 minutes and 45 seconds ago).
        """

        logger.info(f"log_new_activity: {new_activity=} {new_activity_offset=}")

        context = load_contex()
        response = await commit_new_activity(new_activity, context)
        save_contex(context)

        # response = f"я записал, что начал активность '{new_activity}'"
        #
        # if new_activity_offset:
        #     dt_offset = datetime.strptime(new_activity_offset, "%H:%M:%S")
        #     delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)
        #     delta_minutes = delta.seconds / 60
        #     response += f" {delta_minutes:.2f} минут назад"

        return response

    async def log_end_activity(
        self,
        end_activity_offset: str | None = None,
    ) -> str:
        """Log an activity event that ended.
        Use this tool only if the user has stated that an activity is finished AND has NOT mentioned being currently
        engaged in another activity or just starting one.

        Args:
            end_activity_offset: Time since activity ended (optional). Provide this only if the user explicitly
                mentioned how long ago the activity ended. The value must be in the %H:%M:%S format —
                for example: "00:10:45" (10 minutes and 45 seconds ago).
        """

        logger.info(f"log_end_activity: {end_activity_offset=}")

        context = load_contex()
        response = await commit_end_activity(context)
        save_contex(context)

        # response = "я записал, что закончил активность"
        #
        # dt_offset = datetime.strptime(end_activity_offset or "00:00:00", "%H:%M:%S")
        # delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)
        # delta_minutes = delta.seconds / 60
        #
        # if delta_minutes:
        #     response += f" {delta_minutes:.2f} минут назад"

        return response


if __name__ == "__main__":
    init_db()
    mcp = MCPServer()
    mcp.run(transport="sse")
