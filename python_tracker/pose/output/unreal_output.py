from pose.output.output import Output
from pose.transport.websocket_client import WebSocketClient


class UnrealOutput(Output):
    """Prepares narration messages for Unreal Engine."""

    def __init__(self, client: WebSocketClient) -> None:
        self._client = client

    def present(self, narration: str) -> None:
        raise NotImplementedError

    def _build_message(
        self,
        narration: str,
    ) -> str:
        ...