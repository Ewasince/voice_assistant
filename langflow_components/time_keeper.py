from langflow.custom import Component
from langflow.inputs import MessageTextInput
from langflow.io import Output
from langflow.schema import Data


class TimeKeeperComponent(Component):
    display_name = "Time Keeper"
    description = "Write activity events"
    icon = "DarthVader"

    inputs = [
        MessageTextInput(
            name="activity",
            display_name="Activity",
            info="Description of activity",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="result", type_=Data, method="write_activity"),
    ]

    def write_activity(self) -> Data:
        """Evaluate the mathematical expression and return the result."""

        return Data(data={"result": "im wrote activity! "})


    def build(self):
        """Return the main evaluation function."""
        return self.evaluate_expression
