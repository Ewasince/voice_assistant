from datetime import datetime, timedelta

from langflow.custom import Component
from langflow.inputs import MessageTextInput
from langflow.io import Output
from langflow.schema import Data


class TKNewActivityComponent(Component):
    display_name = "TK New Activity"
    description = "Log a new activity event. Trigger this tool when the user indicates they are currently engaged in an activity or have just started one."
    icon = "Radio"

    inputs = [
        MessageTextInput(
            name="new_activity",
            display_name="Activity",
            info="Name of the started activity. Should be short, precise, and sound natural to a human — like a familiar, conventional label for the activity. Avoid synonyms, verb forms, or uncommon phrasings.",
            tool_mode=True,
        ),
        MessageTextInput(
            name="new_activity_offset",
            display_name="Activity Offset",
            info="Time since activity started (optional). Provide this only if the user explicitly mentioned how long ago the activity began. The value must be in the %H:%M:%S format — for example: \"00:10:45\" (10 minutes and 45 seconds ago).",
            tool_mode=True,
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="result", type_=Data, method="write_new_activity"),
    ]

    def write_new_activity(self) -> Data:
        response = f"я записал, что начал активность '{self.new_activity}'"

        if self.new_activity_offset:
            dt_offset = datetime.strptime(self.new_activity_offset, "%H:%M:%S")
            delta = timedelta(hours=dt_offset.hour, minutes=dt_offset.minute, seconds=dt_offset.second)
            delta_minutes = delta.seconds / 60
            response += f" {delta_minutes:.2f} минут назад"

        return Data(data={"result": response})

    def build(self):
        return self.write_new_activity
