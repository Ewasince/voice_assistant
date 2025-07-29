from voxmind.app_utils.settings import Settings


class VASettings(Settings):
    debug_mode: bool = False

    langflow_flow_id: str
    langflow_session_id: str = "default_session"
