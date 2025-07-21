from datetime import datetime, timedelta

from langflow.custom import Component
from langflow.inputs import MessageTextInput
from langflow.io import Output
from langflow.schema import Data


class TKOldActivityComponent(Component):
    display_name = "TK Old Activity"
    description = "Log an activity event that ended. Use this tool only if the user has stated that an activity is finished AND has NOT mentioned being currently engaged in another activity or just starting one."
    icon = "Radio"

    inputs = [
        MessageTextInput(
            name="old_activity_offset",
            display_name="Activity Offset",
            info="Time since activity ended (optional). Provide this only if the user explicitly mentioned how long ago the activity ended. The value must be in the %H:%M:%S format — for example: \"00:10:45\" (10 minutes and 45 seconds ago).",
            tool_mode=True,
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="result", type_=Data, method="write_old_activity"),
    ]

    def write_old_activity(self) -> Data:
        response = f"я записал, что закончил активность"

        dt_offset = datetime.strptime(self.old_activity_offset or "00:00:00", "%H:%M:%S")
        delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)
        delta_minutes = delta.seconds / 60

        if delta_minutes:
            response += f" {delta_minutes:.2f} минут назад"

        return Data(data={"result": response})

    def build(self):
        return self.write_old_activity
