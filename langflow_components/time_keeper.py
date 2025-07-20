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
            name="start_activity",
            display_name="Activity",
            info="pass information about the activity that has started, if applicable",
            tool_mode=True,
            required=False,
        ),
        MessageTextInput(
            name="end_activity",
            display_name="Activity",
            info="pass information about the activity that has ended, if applicable.",
            tool_mode=True,
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="result", type_=Data, method="write_activity"),
    ]

    def write_activity(self) -> Data:
        """Evaluate the mathematical expression and return the result."""

        results = []

        if self.end_activity:
            results.append(f"wrote activity '{self.end_activity}'")
        if self.start_activity:
            results.append(f"started new activity '{self.start_activity}'")

        if not results:
            result = "I did nothing"
        else:
            result = ", ".join(results)
            result = f"i'm {result}"

        return Data(data={"result": result})


    def build(self):
        """Return the main evaluation function."""
        return self.evaluate_expression
