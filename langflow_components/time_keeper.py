from langflow.custom import Component
from langflow.inputs import MessageTextInput
from langflow.io import Output
from langflow.schema import Data


class TKNewActivityComponent(Component):
    display_name = "TK New Activity"
    description = "Write new activity events"
    icon = "Radio"

    inputs = [
        MessageTextInput(
            name="new_activity",
            display_name="Activity",
            info="current or newly started activity. Describe it in a short, precise phrase—ideally a single word, with no synonyms or variations.",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="result", type_=Data, method="write_new_activity"),
    ]

    def write_new_activity(self) -> Data:
        response = f"я записал, что начал активность '{self.new_activity}'"
        print(response)

        return Data(data={"result": response})

    def build(self):
        return self.write_new_activity
